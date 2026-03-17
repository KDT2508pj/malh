from __future__ import annotations

from datetime import datetime
import logging
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from core.config import settings
from models.audio_recording import AudioRecording
from models.interview_session import InterviewSession
from services.storage_cleanup_service import prune_empty_audio_tree, remove_session_audio_tree

logger = logging.getLogger(__name__)


def purge_interview_audio_files(db: Session, inter_id: int) -> dict[str, int]:
    rows = db.query(AudioRecording.file_path).filter(AudioRecording.inter_id == inter_id).all()
    removed_files = sum(1 for row in rows if (row.file_path or "").strip())
    remove_session_audio_tree(Path(settings.STORAGE_DIR), inter_id)

    removed_audio = (
        db.query(AudioRecording)
        .filter(AudioRecording.inter_id == inter_id)
        .delete(synchronize_session=False)
    )
    db.commit()
    prune_empty_audio_tree(Path(settings.STORAGE_DIR))
    return {
        "removed_audio": int(removed_audio),
        "removed_files": int(removed_files),
    }


def clear_completed_session_audio_files(db: Session, inter_id: int) -> dict[str, int]:
    rows = db.query(AudioRecording.file_path).filter(AudioRecording.inter_id == inter_id).all()
    removed_files = sum(1 for row in rows if (row.file_path or "").strip())
    remove_session_audio_tree(Path(settings.STORAGE_DIR), inter_id)

    cleared_audio = (
        db.query(AudioRecording)
        .filter(AudioRecording.inter_id == inter_id, AudioRecording.file_path != "")
        .update(
            {
                AudioRecording.file_path: "",
                AudioRecording.mime_type: None,
                AudioRecording.size_bytes: None,
            },
            synchronize_session=False,
        )
    )
    db.commit()
    prune_empty_audio_tree(Path(settings.STORAGE_DIR))
    return {
        "cleared_audio": int(cleared_audio),
        "removed_files": int(removed_files),
    }


def cleanup_expired_interview_audio(
    db: Session,
    stale_before: datetime,
) -> dict[str, int]:
    in_progress_rows = (
        db.query(
            AudioRecording.inter_id.label("inter_id"),
            func.max(AudioRecording.updated_at).label("last_audio_at"),
        )
        .join(InterviewSession, InterviewSession.inter_id == AudioRecording.inter_id)
        .filter(InterviewSession.inter_status == "IN_PROGRESS")
        .group_by(AudioRecording.inter_id)
        .all()
    )

    stale_in_progress_session_ids = [
        int(row.inter_id)
        for row in in_progress_rows
        if row.last_audio_at and row.last_audio_at <= stale_before
    ]
    done_rows = (
        db.query(AudioRecording.inter_id.label("inter_id"))
        .join(InterviewSession, InterviewSession.inter_id == AudioRecording.inter_id)
        .filter(
            InterviewSession.inter_status == "DONE",
            InterviewSession.inter_finished_at.is_not(None),
            InterviewSession.inter_finished_at <= stale_before,
            AudioRecording.file_path != "",
        )
        .group_by(AudioRecording.inter_id)
        .all()
    )
    expired_done_session_ids = [int(row.inter_id) for row in done_rows]
    summary = {
        "stale_in_progress_sessions": 0,
        "expired_done_sessions": 0,
        "removed_audio_rows": 0,
        "cleared_audio_rows": 0,
        "removed_files": 0,
    }

    for inter_id in stale_in_progress_session_ids:
        try:
            result = purge_interview_audio_files(db=db, inter_id=inter_id)
        except Exception:
            db.rollback()
            logger.exception("STALE_IN_PROGRESS_AUDIO_CLEANUP_FAILED inter_id=%s", inter_id)
            continue

        summary["stale_in_progress_sessions"] += 1
        summary["removed_audio_rows"] += int(result["removed_audio"])
        summary["removed_files"] += int(result["removed_files"])

    for inter_id in expired_done_session_ids:
        try:
            result = clear_completed_session_audio_files(db=db, inter_id=inter_id)
        except Exception:
            db.rollback()
            logger.exception("EXPIRED_DONE_AUDIO_CLEANUP_FAILED inter_id=%s", inter_id)
            continue

        summary["expired_done_sessions"] += 1
        summary["cleared_audio_rows"] += int(result["cleared_audio"])
        summary["removed_files"] += int(result["removed_files"])

    return summary
