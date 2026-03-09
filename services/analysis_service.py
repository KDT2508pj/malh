import json
import os

from openai import OpenAI
from sqlalchemy.orm import Session, joinedload

from models.answer_analysis import AnswerAnalysis
from models.interview_session import InterviewSession
from models.select_question import SelectQuestion
from models.transcript import Transcript
from services.prompt.analysis.answer_analysis_prompt import ANSWER_ANALYSIS_SYSTEM_PROMPT
from schemas.answer_analysis_schema import (
    AnswerAnalysisLLMResult,
    get_answer_analysis_response_format,
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _limit_text(text: str | None, max_length: int = 12000) -> str:
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_length:
        return text
    return text[:max_length] + "\n...(truncated)"


def _pick_answer_text(select_question: SelectQuestion) -> str:
    transcript = select_question.transcript
    if not transcript:
        raise ValueError("Transcript가 없습니다.")

    refine = transcript.transcript_refine
    if refine and refine.r_refined_text and refine.r_refined_text.strip():
        return refine.r_refined_text.strip()

    if transcript.transcript_text and transcript.transcript_text.strip():
        return transcript.transcript_text.strip()

    raise ValueError("분석할 답변 텍스트가 없습니다.")


def _pick_resume_text(select_question: SelectQuestion) -> str:
    interview_session = select_question.interview_session
    if not interview_session or not interview_session.resume:
        raise ValueError("Resume이 없습니다.")

    resume_text = interview_session.resume.resume_extracted_text
    if not resume_text or not resume_text.strip():
        raise ValueError("resume_extracted_text가 없습니다.")

    return resume_text.strip()


def _compute_overall_score(
    relevance_score: int,
    coverage_score: int,
    specificity_score: int,
    evidence_score: int,
    consistency_score: int,
) -> int:
    score = (
        relevance_score * 0.30
        + coverage_score * 0.25
        + specificity_score * 0.15
        + evidence_score * 0.15
        + consistency_score * 0.15
    )
    return round(score)


def _derive_weaknesses(result: AnswerAnalysisLLMResult) -> list[str]:
    threshold = 70
    weaknesses = []

    if result.relevance_score < threshold:
        weaknesses.append("RELEVANCE")
    if result.coverage_score < threshold:
        weaknesses.append("COVERAGE")
    if result.specificity_score < threshold:
        weaknesses.append("SPECIFICITY")
    if result.evidence_score < threshold:
        weaknesses.append("EVIDENCE")
    if result.consistency_score < threshold:
        weaknesses.append("CONSISTENCY")

    return weaknesses


def _build_user_prompt(
    question_text: str,
    question_evidence: list,
    answer_text: str,
    resume_text: str,
) -> str:
    return f"""
[질문]
{question_text}

[질문 근거]
{json.dumps(question_evidence, ensure_ascii=False)}

[정제 답변]
{_limit_text(answer_text, 6000)}

[이력서 추출 텍스트]
{_limit_text(resume_text, 10000)}
""".strip()


def analyze_answer_by_sel_id(
    db: Session,
    sel_id: int,
    model: str = "gpt-4o-mini",
) -> AnswerAnalysis:
    select_question = (
        db.query(SelectQuestion)
        .options(
            joinedload(SelectQuestion.question),
            joinedload(SelectQuestion.transcript).joinedload(Transcript.transcript_refine),
            joinedload(SelectQuestion.interview_session).joinedload(InterviewSession.resume),
            joinedload(SelectQuestion.answer_analysis),
        )
        .filter(SelectQuestion.sel_id == sel_id)
        .first()
    )

    if not select_question:
        raise ValueError(f"sel_id={sel_id} 질문을 찾을 수 없습니다.")
    if not select_question.question:
        raise ValueError("Question이 없습니다.")

    question_text = select_question.question.qust_question_text
    question_evidence = select_question.question.qust_evidence or []
    answer_text = _pick_answer_text(select_question)
    resume_text = _pick_resume_text(select_question)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": ANSWER_ANALYSIS_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": _build_user_prompt(
                    question_text=question_text,
                    question_evidence=question_evidence,
                    answer_text=answer_text,
                    resume_text=resume_text,
                ),
            },
        ],
        response_format=get_answer_analysis_response_format(),
    )

    message = response.choices[0].message
    if getattr(message, "refusal", None):
        raise ValueError(f"LLM 분석이 거절되었습니다: {message.refusal}")

    content = message.content
    if not content:
        raise ValueError("LLM 응답이 비어 있습니다.")

    parsed = AnswerAnalysisLLMResult.model_validate(json.loads(content))

    overall_score = _compute_overall_score(
        relevance_score=parsed.relevance_score,
        coverage_score=parsed.coverage_score,
        specificity_score=parsed.specificity_score,
        evidence_score=parsed.evidence_score,
        consistency_score=parsed.consistency_score,
    )
    weaknesses = _derive_weaknesses(parsed)

    analysis = select_question.answer_analysis
    if analysis is None:
        analysis = AnswerAnalysis(sel_id=sel_id)
        db.add(analysis)

    analysis.anal_overall_score = overall_score
    analysis.anal_relevance_score = parsed.relevance_score
    analysis.anal_coverage_score = parsed.coverage_score
    analysis.anal_specificity_score = parsed.specificity_score
    analysis.anal_evidence_score = parsed.evidence_score
    analysis.anal_consistency_score = parsed.consistency_score
    analysis.anal_weakness = weaknesses

    analysis.anal_relevance_reason = parsed.relevance_reason
    analysis.anal_coverage_reason = parsed.coverage_reason
    analysis.anal_specificity_reason = parsed.specificity_reason
    analysis.anal_evidence_reason = parsed.evidence_reason
    analysis.anal_consistency_reason = parsed.consistency_reason
    analysis.anal_good_points = [item.model_dump() for item in parsed.good_points]
    analysis.anal_improvement_points = [item.model_dump() for item in parsed.improvement_points]
    analysis.anal_overall_comment = parsed.overall_comment
    analysis.anal_revised_answer = parsed.revised_answer
    analysis.anal_llm_model = model

    db.commit()
    db.refresh(analysis)
    return analysis