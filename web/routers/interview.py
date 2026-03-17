import threading
import time

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from core.database import get_db, SessionLocal
from models.audio_recording import AudioRecording
from models.interview_session import InterviewSession
from models.question import Question
from models.select_question import SelectQuestion
from models.transcript import Transcript
from services.analysis_service import analyze_answer_by_sel_id
from services.speech_feedback_service import (
    generate_speech_feedback,
    get_speech_feedback,
    parse_stream_feedback_markdown,
    start_speech_feedback_stream,
    upsert_speech_feedback,
)
from services.speech_score_service import (
    calculate_speech_scores,
    get_speech_detail_payload,
    upsert_speech_detail,
    upsert_speech_summary,
)
from services.stt_service import run_stt_and_update, save_recording_and_upsert
from web.common import (
    SUBMIT_ANALYSIS_LOCK,
    SUBMIT_ANALYSIS_PROGRESS,
    SUBMIT_ANALYSIS_TIMEOUT_SEC,
    _get_question_analysis_progress,
    _get_resume_id_by_session,
    _get_session_recording_counts,
    _invalidate_cached_weakness_report,
    _is_question_analysis_complete,
    _load_session_question_items,
    _refresh_session_status_if_ready,
    _reset_session_attempt_data,
    _update_question_analysis_progress,
    _update_submit_progress,
    templates,
)

router = APIRouter()


def _analyze_single_question(db: Session, inter_id: int, sel_id: int) -> None:
    row = (
        db.query(
            SelectQuestion.sel_id,
            SelectQuestion.sel_order_no,
            Question.qust_question_text,
            AudioRecording.file_path,
            AudioRecording.duration_sec,
            Transcript.transcript_text,
        )
        .join(Question, Question.qust_id == SelectQuestion.qust_id)
        .outerjoin(AudioRecording, AudioRecording.sel_id == SelectQuestion.sel_id)
        .outerjoin(Transcript, Transcript.sel_id == SelectQuestion.sel_id)
        .filter(SelectQuestion.inter_id == inter_id, SelectQuestion.sel_id == sel_id)
        .first()
    )
    if not row:
        raise RuntimeError("질문을 찾을 수 없습니다.")
    if not (row.file_path or "").strip():
        raise RuntimeError("녹음 파일이 없습니다.")

    transcript_text = (row.transcript_text or "").strip()
    if not transcript_text:
        _, transcript = run_stt_and_update(db=db, inter_id=inter_id, sel_id=sel_id)
        transcript_text = (transcript.transcript_text or "").strip()
    if not transcript_text:
        raise RuntimeError("전사 텍스트를 생성하지 못했습니다.")

    score_payload = calculate_speech_scores(
        transcript_text=transcript_text,
        duration_sec=int(row.duration_sec or 0),
        question_text=row.qust_question_text,
    )
    upsert_speech_summary(db=db, sel_id=sel_id, score=score_payload)
    upsert_speech_detail(db=db, sel_id=sel_id, score=score_payload)
    analyze_answer_by_sel_id(db=db, sel_id=sel_id, model="gpt-4o-mini")
    _refresh_session_status_if_ready(db=db, inter_id=inter_id)


def _run_question_analysis_job(inter_id: int, sel_id: int) -> None:
    db = SessionLocal()
    try:
        _update_question_analysis_progress(
            inter_id,
            sel_id,
            status="running",
            done=False,
            ok=False,
            started_at=int(time.time()),
        )
        _analyze_single_question(db=db, inter_id=inter_id, sel_id=sel_id)
        _update_question_analysis_progress(
            inter_id,
            sel_id,
            status="done",
            done=True,
            ok=True,
            finished_at=int(time.time()),
        )
    except Exception as exc:
        db.rollback()
        _update_question_analysis_progress(
            inter_id,
            sel_id,
            status="failed",
            done=True,
            ok=False,
            message=str(exc),
            finished_at=int(time.time()),
        )
    finally:
        db.close()


def _start_question_analysis_job(inter_id: int, sel_id: int) -> bool:
    progress = _get_question_analysis_progress(inter_id, sel_id)
    if progress.get("status") == "running":
        return False
    threading.Thread(target=_run_question_analysis_job, args=(inter_id, sel_id), daemon=True).start()
    return True


def _wait_for_question_analysis(db: Session, inter_id: int, sel_id: int, timeout_sec: float) -> bool:
    deadline = time.monotonic() + max(0.5, timeout_sec)
    while time.monotonic() < deadline:
        db.expire_all()
        if _is_question_analysis_complete(db=db, sel_id=sel_id):
            return True
        progress = _get_question_analysis_progress(inter_id, sel_id)
        if progress.get("done"):
            return bool(progress.get("ok")) and _is_question_analysis_complete(db=db, sel_id=sel_id)
        time.sleep(0.25)
    return False


def _run_submit_analysis_job(inter_id: int) -> None:
    db = SessionLocal()
    try:
        job_started = time.monotonic()
        rows = (
            db.query(
                SelectQuestion.sel_id,
                SelectQuestion.sel_order_no,
                Question.qust_question_text,
                AudioRecording.file_path,
            )
            .join(Question, Question.qust_id == SelectQuestion.qust_id)
            .outerjoin(AudioRecording, AudioRecording.sel_id == SelectQuestion.sel_id)
            .filter(SelectQuestion.inter_id == inter_id)
            .order_by(SelectQuestion.sel_order_no.asc())
            .all()
        )
        total = len(rows)
        if total == 0:
            _update_submit_progress(
                inter_id,
                status="failed",
                done=True,
                ok=False,
                total=0,
                message="면접 세션 질문을 찾을 수 없습니다.",
            )
            return

        _update_submit_progress(
            inter_id,
            status="running",
            total=total,
            completed=0,
            failed_count=0,
            message="분석을 시작합니다.",
            done=False,
            ok=False,
        )

        processed: list[dict[str, int]] = []
        failed: list[dict[str, object]] = []

        for index, row in enumerate(rows, start=1):
            if time.monotonic() - job_started > SUBMIT_ANALYSIS_TIMEOUT_SEC:
                for pending in rows[index - 1:]:
                    failed.append(
                        {
                            "sel_id": int(pending.sel_id),
                            "sel_order_no": int(pending.sel_order_no),
                            "reason": "시간 초과",
                        }
                    )
                break

            sel_id = int(row.sel_id)
            sel_order_no = int(row.sel_order_no)
            _update_submit_progress(inter_id, current_index=index, message=f"Q{sel_order_no} 분석 중..")

            if not (row.file_path or "").strip():
                failed.append({"sel_id": sel_id, "sel_order_no": sel_order_no, "reason": "녹음 없음"})
                continue

            try:
                if _is_question_analysis_complete(db=db, sel_id=sel_id):
                    processed.append({"sel_id": sel_id, "sel_order_no": sel_order_no})
                    _update_submit_progress(inter_id, completed=len(processed), message=f"Q{sel_order_no} 완료")
                    continue

                progress = _get_question_analysis_progress(inter_id, sel_id)
                if progress.get("status") == "running":
                    remaining_timeout = SUBMIT_ANALYSIS_TIMEOUT_SEC - (time.monotonic() - job_started)
                    if _wait_for_question_analysis(db=db, inter_id=inter_id, sel_id=sel_id, timeout_sec=remaining_timeout):
                        processed.append({"sel_id": sel_id, "sel_order_no": sel_order_no})
                        _update_submit_progress(inter_id, completed=len(processed), message=f"Q{sel_order_no} 완료")
                        continue

                _analyze_single_question(db=db, inter_id=inter_id, sel_id=sel_id)
                processed.append({"sel_id": sel_id, "sel_order_no": sel_order_no})
                _update_submit_progress(inter_id, completed=len(processed), message=f"Q{sel_order_no} 완료")
            except Exception as exc:
                db.rollback()
                failed.append({"sel_id": sel_id, "sel_order_no": sel_order_no, "reason": str(exc)})

        session = db.query(InterviewSession).filter(InterviewSession.inter_id == inter_id).first()
        if session and not failed:
            session.inter_status = "DONE"
            session.inter_finished_at = func.now()
            db.commit()

        all_failed = total > 0 and len(failed) == total
        reset_summary = _reset_session_attempt_data(db=db, inter_id=inter_id) if all_failed else None
        _update_submit_progress(
            inter_id,
            status="done",
            done=True,
            ok=len(failed) == 0,
            completed=len(processed),
            processed_count=len(processed),
            failed_count=len(failed),
            failed=failed,
            reset_applied=all_failed,
            reset_summary=reset_summary,
            message="분석이 완료되었습니다." if not failed else "일부 실패",
            finished_at=int(time.time()),
        )
    except Exception as exc:
        db.rollback()
        _update_submit_progress(
            inter_id,
            status="failed",
            done=True,
            ok=False,
            message=f"실패: {exc}",
            finished_at=int(time.time()),
        )
    finally:
        db.close()


@router.get("/interviews/{session_id}/wait")
async def interview_wait(request: Request, session_id: int):
    return templates.TemplateResponse("interview/wait.html", {"request": request, "session_id": session_id})


@router.get("/interviews/{session_id}")
async def interview_questions(request: Request, session_id: int, db: Session = Depends(get_db)):
    items = _load_session_question_items(db=db, session_id=session_id)
    return templates.TemplateResponse(
        "interview/questions.html",
        {
            "request": request,
            "session_id": session_id,
            "resume_id": _get_resume_id_by_session(db, session_id),
            "question_items": items,
            "total_questions": len(items),
            "recorded_questions": sum(1 for item in items if item["is_recorded"]),
        },
    )


@router.get("/interviews/{session_id}/submit-loading")
async def interview_submit_loading(request: Request, session_id: int):
    return templates.TemplateResponse("interview/submit_loading.html", {"request": request, "session_id": session_id})


@router.get("/interviews/{session_id}/questions/{question_id}")
async def interview_question_detail(request: Request, session_id: int, question_id: int, db: Session = Depends(get_db)):
    row = (
        db.query(
            SelectQuestion.sel_id,
            SelectQuestion.sel_order_no,
            Question.qust_question_text.label("question_text"),
            AudioRecording.recording_id.label("recording_id"),
        )
        .join(Question, Question.qust_id == SelectQuestion.qust_id)
        .outerjoin(AudioRecording, AudioRecording.sel_id == SelectQuestion.sel_id)
        .filter(SelectQuestion.inter_id == session_id, SelectQuestion.sel_id == question_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="질문을 찾을 수 없습니다.")
    return templates.TemplateResponse(
        "interview/question_detail.html",
        {
            "request": request,
            "session_id": session_id,
            "question_id": question_id,
            "question_item": {
                "sel_id": row.sel_id,
                "sel_order_no": row.sel_order_no,
                "question_text": row.question_text,
                "is_recorded": row.recording_id is not None,
            },
        },
    )


@router.post("/interviews/{inter_id}/questions/{sel_id}/recordings", status_code=status.HTTP_201_CREATED)
async def upload_recording(
    inter_id: int,
    sel_id: int,
    audio_file: UploadFile = File(...),
    duration_sec: int | None = Form(default=None),
    db: Session = Depends(get_db),
):
    if not audio_file.content_type or not audio_file.content_type.startswith("audio/"):
        raise HTTPException(status_code=415, detail="오디오 파일만 업로드할 수 있습니다.")

    sel = db.query(SelectQuestion).filter(SelectQuestion.sel_id == sel_id, SelectQuestion.inter_id == inter_id).first()
    if not sel:
        raise HTTPException(status_code=404, detail="질문이 없습니다.")

    existing_recording = (
        db.query(AudioRecording.recording_id)
        .filter(AudioRecording.sel_id == sel_id, AudioRecording.inter_id == inter_id)
        .first()
    )
    if existing_recording:
        raise HTTPException(status_code=409, detail="이미 녹음이 완료된 질문입니다. 재녹음은 지원하지 않습니다.")

    payload = await audio_file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="빈 파일입니다.")

    saved = save_recording_and_upsert(
        db=db,
        inter_id=inter_id,
        sel_id=sel_id,
        filename=audio_file.filename,
        content_type=audio_file.content_type,
        payload=payload,
        duration_sec=duration_sec,
    )
    _invalidate_cached_weakness_report(inter_id)
    _start_question_analysis_job(inter_id=inter_id, sel_id=sel_id)
    return {"message": "Recording uploaded.", "recording_id": saved.recording_id}


@router.post("/interviews/{inter_id}/questions/{sel_id}/stt")
async def run_stt(inter_id: int, sel_id: int, db: Session = Depends(get_db)):
    try:
        _, transcript = run_stt_and_update(db=db, inter_id=inter_id, sel_id=sel_id)
        _invalidate_cached_weakness_report(inter_id)
        return {"message": "STT completed.", "transcript_text": transcript.transcript_text}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/interviews/{inter_id}/questions/{sel_id}/speech-score")
async def build_speech_score(inter_id: int, sel_id: int, db: Session = Depends(get_db)):
    row = (
        db.query(
            SelectQuestion.sel_id,
            Question.qust_question_text,
            AudioRecording.duration_sec,
            Transcript.transcript_text,
        )
        .join(Question, Question.qust_id == SelectQuestion.qust_id)
        .outerjoin(AudioRecording, AudioRecording.sel_id == SelectQuestion.sel_id)
        .outerjoin(Transcript, Transcript.sel_id == SelectQuestion.sel_id)
        .filter(SelectQuestion.inter_id == inter_id, SelectQuestion.sel_id == sel_id)
        .first()
    )
    if not row or not (row.transcript_text or "").strip():
        raise HTTPException(status_code=400, detail="데이터 부족")

    score_payload = calculate_speech_scores(
        transcript_text=row.transcript_text,
        duration_sec=int(row.duration_sec or 0),
        question_text=row.qust_question_text,
    )
    summary = upsert_speech_summary(db=db, sel_id=sel_id, score=score_payload)
    upsert_speech_detail(db=db, sel_id=sel_id, score=score_payload)
    _invalidate_cached_weakness_report(inter_id)
    return {"message": "Speech score calculated.", "score_id": summary.score_id}


@router.post("/interviews/{inter_id}/submit-analysis/start", status_code=status.HTTP_202_ACCEPTED)
async def start_submit_analysis_job(inter_id: int, db: Session = Depends(get_db)):
    total, recorded = _get_session_recording_counts(db=db, session_id=inter_id)
    if total != 5 or recorded < 5:
        raise HTTPException(status_code=400, detail=f"5개 녹음이 필요합니다. (현재 {recorded}/{total})")

    with SUBMIT_ANALYSIS_LOCK:
        if SUBMIT_ANALYSIS_PROGRESS.get(inter_id, {}).get("status") == "running":
            return {"ok": True, "status": "running"}
        SUBMIT_ANALYSIS_PROGRESS[inter_id] = {
            "status": "running",
            "done": False,
            "ok": False,
            "started_at": int(time.time()),
        }
    threading.Thread(target=_run_submit_analysis_job, args=(inter_id,), daemon=True).start()
    return {"ok": True, "status": "started"}


@router.get("/interviews/{inter_id}/submit-analysis/progress")
async def get_submit_analysis_progress(inter_id: int):
    with SUBMIT_ANALYSIS_LOCK:
        progress = dict(SUBMIT_ANALYSIS_PROGRESS.get(inter_id, {}))
        if progress.get("status") == "running" and (
            int(time.time()) - int(progress.get("started_at", 0))
        ) > SUBMIT_ANALYSIS_TIMEOUT_SEC:
            progress.update({"status": "failed", "done": True, "message": "시간 초과"})
            SUBMIT_ANALYSIS_PROGRESS[inter_id] = progress

    if not progress:
        raise HTTPException(status_code=404, detail="Job not found")

    total = int(progress.get("total", 0))
    completed = int(progress.get("completed", 0))
    progress["percent"] = int((completed / total) * 100) if total > 0 else 0
    return progress


@router.post("/interviews/{inter_id}/questions/{sel_id}/speech-feedback")
async def build_speech_feedback(inter_id: int, sel_id: int, force: int = Form(default=0), db: Session = Depends(get_db)):
    if force == 0:
        existing = get_speech_feedback(db=db, sel_id=sel_id)
        if existing:
            return {
                "report_md": existing.sfb_report_md,
                "coaching_md": existing.sfb_coaching_md,
                "model": existing.sfb_model,
            }

    row = db.query(Question.qust_question_text).join(SelectQuestion).filter(SelectQuestion.sel_id == sel_id).first()
    score_payload = get_speech_detail_payload(db=db, sel_id=sel_id)
    if not score_payload:
        raise HTTPException(status_code=409, detail="지표가 없습니다.")

    try:
        res = generate_speech_feedback(question_text=row.qust_question_text or "", score_payload=score_payload)
        upsert_speech_feedback(db=db, sel_id=sel_id, result=res)
        return {"report_md": res.report_md, "coaching_md": res.coaching_md, "model": res.model}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/interviews/{inter_id}/questions/{sel_id}/speech-feedback/stream")
async def build_speech_feedback_stream(inter_id: int, sel_id: int, force: int = Form(default=0), db: Session = Depends(get_db)):
    row = db.query(Question.qust_question_text).join(SelectQuestion).filter(SelectQuestion.sel_id == sel_id).first()
    score_payload = get_speech_detail_payload(db=db, sel_id=sel_id)
    if not score_payload:
        raise HTTPException(status_code=409, detail="지표가 없습니다.")

    def stream_generator():
        try:
            stream, model = start_speech_feedback_stream(
                question_text=row.qust_question_text or "",
                score_payload=score_payload,
            )
            full_text = ""
            for part in stream:
                delta = getattr(part.choices[0].delta, "content", "")
                if delta:
                    full_text += delta
                    yield delta
            upsert_speech_feedback(
                db=db,
                sel_id=sel_id,
                result=parse_stream_feedback_markdown(content=full_text, model=model),
            )
        except Exception as exc:
            yield f"오류: {exc}"

    return StreamingResponse(stream_generator(), media_type="text/plain; charset=utf-8")
