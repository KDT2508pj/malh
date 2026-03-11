from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Any

from sqlalchemy.orm import Session

from models.answer_analysis import AnswerAnalysis
from models.select_question import SelectQuestion


WEAKNESS_LABEL_MAP = {
    "RELEVANCE": "질문 적합성 부족",
    "COVERAGE": "답변 내용 보강 필요",
    "SPECIFICITY": "답변의 구체성 부족",
    "EVIDENCE": "경험·사례 근거 부족",
    "CONSISTENCY": "이력서 일관성 부족",
}

WEAKNESS_FALLBACK_SUMMARY_MAP = {
    "RELEVANCE": "질문 의도와 직접 연결되는 답변이 부족한 경우가 반복되었습니다.",
    "COVERAGE": "질문에서 요구한 핵심 요소를 충분히 담지 못한 답변이 있었습니다.",
    "SPECIFICITY": "설명이 다소 추상적이어서 실제 행동, 기술, 상황이 선명하게 드러나지 않았습니다.",
    "EVIDENCE": "프로젝트 경험, 사례, 결과 수치 등 근거가 부족한 답변이 있었습니다.",
    "CONSISTENCY": "답변 내용과 이력서 기반 경험의 연결이 약한 경우가 있었습니다.",
}

WEAKNESS_FALLBACK_TIP_MAP = {
    "RELEVANCE": "질문의 핵심 키워드를 먼저 짚고, 그에 맞는 경험이나 설명을 바로 연결해 주세요.",
    "COVERAGE": "질문에서 요구한 항목을 2~3개로 나눈 뒤 빠짐없이 순서대로 답변해 주세요.",
    "SPECIFICITY": "상황-행동-결과 순서로 설명하고, 사용한 기술이나 본인 역할을 함께 말해 주세요.",
    "EVIDENCE": "실제 프로젝트 사례, 문제 해결 방식, 결과 수치나 변화까지 함께 제시해 주세요.",
    "CONSISTENCY": "이력서에 적은 경험과 연결되는 사례를 선택해 답변하면 신뢰도가 높아집니다.",
}


def _parse_json_field(value: Any, default: Any) -> Any:
    if value is None:
        return default

    if isinstance(value, (list, dict)):
        return value

    if isinstance(value, str):
        value = value.strip()
        if not value:
            return default
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return default

    return default


def _clean_text(text: str | None) -> str:
    if not text:
        return ""
    return " ".join(text.strip().split())


def _metric_score(analysis: AnswerAnalysis, metric: str) -> int:
    metric_score_map = {
        "RELEVANCE": analysis.anal_relevance_score,
        "COVERAGE": analysis.anal_coverage_score,
        "SPECIFICITY": analysis.anal_specificity_score,
        "EVIDENCE": analysis.anal_evidence_score,
        "CONSISTENCY": analysis.anal_consistency_score,
    }
    score = metric_score_map.get(metric, 0)
    return int(score or 0)


def _metric_reason(analysis: AnswerAnalysis, metric: str) -> str:
    metric_reason_map = {
        "RELEVANCE": analysis.anal_relevance_reason,
        "COVERAGE": analysis.anal_coverage_reason,
        "SPECIFICITY": analysis.anal_specificity_reason,
        "EVIDENCE": analysis.anal_evidence_reason,
        "CONSISTENCY": analysis.anal_consistency_reason,
    }
    return _clean_text(metric_reason_map.get(metric))


def get_session_weakness_top3(db: Session, session_id: int, top_k: int = 3) -> list[dict[str, Any]]:
    rows = (
        db.query(AnswerAnalysis, SelectQuestion.sel_order_no)
        .join(SelectQuestion, AnswerAnalysis.sel_id == SelectQuestion.sel_id)
        .filter(SelectQuestion.inter_id == session_id)
        .order_by(SelectQuestion.sel_order_no.asc())
        .all()
    )

    if not rows:
        return []

    stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "count": 0,
            "severity_sum": 0,
            "related_questions": set(),
            "reasons": Counter(),
            "tips": Counter(),
        }
    )

    for analysis, sel_order_no in rows:
        weakness_metrics = _parse_json_field(analysis.anal_weakness, default=[])
        improvement_points = _parse_json_field(analysis.anal_improvement_points, default=[])

        if not isinstance(weakness_metrics, list):
            continue

        for metric in weakness_metrics:
            if metric not in WEAKNESS_LABEL_MAP:
                continue

            score = _metric_score(analysis, metric)
            severity = max(0, 100 - score)

            stats[metric]["count"] += 1
            stats[metric]["severity_sum"] += severity
            stats[metric]["related_questions"].add(int(sel_order_no))

            reason = _metric_reason(analysis, metric)
            if reason:
                stats[metric]["reasons"][reason] += 1

        if isinstance(improvement_points, list):
            for point in improvement_points:
                if not isinstance(point, dict):
                    continue

                metric = point.get("metric")
                detail = _clean_text(point.get("detail"))

                if metric in WEAKNESS_LABEL_MAP and detail:
                    stats[metric]["tips"][detail] += 1

    result: list[dict[str, Any]] = []

    for metric, stat in stats.items():
        count = stat["count"]
        severity_sum = stat["severity_sum"]

        if count == 0:
            continue

        avg_severity = severity_sum / count
        count_bonus = min((count - 1) * 8, 20)
        importance_score = int(round(min(99, avg_severity + count_bonus)))

        summary = (
            stat["reasons"].most_common(1)[0][0]
            if stat["reasons"]
            else WEAKNESS_FALLBACK_SUMMARY_MAP[metric]
        )

        tip = (
            stat["tips"].most_common(1)[0][0]
            if stat["tips"]
            else WEAKNESS_FALLBACK_TIP_MAP[metric]
        )

        result.append(
            {
                "metric": metric,
                "title": WEAKNESS_LABEL_MAP[metric],
                "summary": summary,
                "related_questions": sorted(stat["related_questions"]),
                "tip": tip,
                "score": importance_score,
                "count": count,
                "severity_sum": severity_sum,
            }
        )

    result.sort(
        key=lambda x: (
            -x["count"],
            -x["severity_sum"],
            -x["score"],
            x["title"],
        )
    )

    return result[:top_k]