from __future__ import annotations

import re
from dataclasses import dataclass
from statistics import pstdev
from typing import Any

from models.speech_score_summary import SpeechScoreSummary
from sqlalchemy.orm import Session


FILLER_WORDS = {
    "음",
    "어",
    "그",
    "저",
    "약간",
    "뭐랄까",
    "그러니까",
    "사실",
}

CONNECTIVE_WORDS = {
    "그리고",
    "그래서",
    "하지만",
    "또한",
    "먼저",
    "다음으로",
    "결과적으로",
    "따라서",
    "반면",
    "즉",
}


@dataclass
class SpeechScoreResult:
    fluency_score: float
    clarity_score: float
    structure_score: float
    length_score: float
    metrics: dict[str, Any]


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _target_band_score(value: float, low: float, high: float, hard_low: float, hard_high: float) -> float:
    if value <= hard_low or value >= hard_high:
        return 0.0
    if low <= value <= high:
        return 100.0
    if value < low:
        return _clamp((value - hard_low) / (low - hard_low) * 100.0, 0.0, 100.0)
    return _clamp((hard_high - value) / (hard_high - high) * 100.0, 0.0, 100.0)


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9가-힣]+", text.lower())


def _split_sentences(text: str) -> list[str]:
    parts = [x.strip() for x in re.split(r"[.!?。？！\n]+", text) if x.strip()]
    return parts


def _quality_ratio(text: str) -> float:
    if not text:
        return 0.0
    total = len(text)
    good = len(re.findall(r"[A-Za-z0-9가-힣\s.,!?%]", text))
    return good / total if total else 0.0


def calculate_speech_scores(transcript_text: str, duration_sec: int) -> SpeechScoreResult:
    clean_text = (transcript_text or "").strip()
    tokens = _tokenize(clean_text)
    word_count = len(tokens)

    sentences = _split_sentences(clean_text)
    if not sentences and clean_text:
        sentences = [clean_text]
    sentence_count = len(sentences)

    duration = max(1, int(duration_sec or 0))
    minutes = duration / 60.0
    wpm = word_count / minutes if minutes > 0 else 0.0

    filler_count = sum(1 for t in tokens if t in FILLER_WORDS)
    filler_ratio = filler_count / max(1, word_count)

    repetition_count = sum(1 for idx in range(1, len(tokens)) if tokens[idx] == tokens[idx - 1])
    repetition_ratio = repetition_count / max(1, word_count - 1)

    sentence_lengths = [max(1, len(_tokenize(s))) for s in sentences] if sentences else [0]
    avg_sentence_len = sum(sentence_lengths) / max(1, sentence_count)
    sentence_len_std = pstdev(sentence_lengths) if len(sentence_lengths) > 1 else 0.0

    connective_count = sum(1 for t in tokens if t in CONNECTIVE_WORDS)
    connective_density = connective_count / max(1, sentence_count)

    # Proxy timing metrics without forced alignment:
    # speaking time is estimated from word count and typical speaking speed.
    est_speaking_time = word_count / 2.4
    silence_total_sec = _clamp(duration - est_speaking_time, 0.0, float(duration))
    pause_count = max(1, sentence_count - 1)
    max_pause_sec = silence_total_sec / pause_count if pause_count > 0 else silence_total_sec
    pause_ratio = silence_total_sec / max(1.0, float(duration))
    speed_variation = sentence_len_std

    pace_score = _target_band_score(wpm, low=95.0, high=165.0, hard_low=45.0, hard_high=240.0)
    filler_score = _clamp(100.0 - filler_ratio * 700.0, 0.0, 100.0)
    repetition_score = _clamp(100.0 - repetition_ratio * 500.0, 0.0, 100.0)
    fluency_score = round(pace_score * 0.5 + filler_score * 0.25 + repetition_score * 0.25, 1)

    text_quality = _quality_ratio(clean_text)
    stt_accuracy = _clamp(0.65 + text_quality * 0.35 - filler_ratio * 0.12 - repetition_ratio * 0.10, 0.0, 1.0)
    pronunciation_clarity = _clamp(stt_accuracy - 0.07 + (pace_score / 100.0) * 0.08, 0.0, 1.0)
    clarity_score = round((stt_accuracy * 100.0) * 0.6 + (pronunciation_clarity * 100.0) * 0.4, 1)
    avg_stt_confidence = _clamp(stt_accuracy - 0.015, 0.0, 1.0)
    articulation_ratio = _clamp(pronunciation_clarity + 0.03, 0.0, 1.0)
    volume_stability = _clamp(2.6 + pace_score / 100.0 * 0.9, 0.0, 4.0)
    clipping_ratio = _clamp((1.0 - text_quality) * 0.02, 0.0, 0.02)

    sentence_len_score = _target_band_score(avg_sentence_len, low=8.0, high=24.0, hard_low=3.0, hard_high=40.0)
    variation_score = _target_band_score(sentence_len_std, low=2.0, high=9.0, hard_low=0.0, hard_high=18.0)
    connective_score = _target_band_score(connective_density, low=0.25, high=1.25, hard_low=0.0, hard_high=2.5)
    structure_score = round(sentence_len_score * 0.45 + variation_score * 0.3 + connective_score * 0.25, 1)

    length_adequacy_score = _target_band_score(float(duration), low=60.0, high=120.0, hard_low=20.0, hard_high=240.0)
    length_score = round(length_adequacy_score * 0.7 + sentence_len_score * 0.3, 1)

    return SpeechScoreResult(
        fluency_score=fluency_score,
        clarity_score=clarity_score,
        structure_score=structure_score,
        length_score=length_score,
        metrics={
            "duration_sec": duration,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "wpm": round(wpm, 1),
            "filler_count": filler_count,
            "filler_ratio": round(filler_ratio, 4),
            "repetition_count": repetition_count,
            "repetition_ratio": round(repetition_ratio, 4),
            "avg_sentence_len": round(avg_sentence_len, 2),
            "sentence_len_std": round(sentence_len_std, 2),
            "connective_count": connective_count,
            "connective_density": round(connective_density, 4),
            "stt_accuracy": round(stt_accuracy, 4),
            "avg_stt_confidence": round(avg_stt_confidence, 4),
            "pronunciation_clarity": round(pronunciation_clarity, 4),
            "articulation_ratio": round(articulation_ratio, 4),
            "volume_stability": round(volume_stability, 2),
            "clipping_ratio": round(clipping_ratio, 4),
            "silence_total_sec": round(silence_total_sec, 2),
            "max_pause_sec": round(max_pause_sec, 2),
            "pause_ratio": round(pause_ratio, 4),
            "pause_count": pause_count,
            "speed_variation": round(speed_variation, 2),
            "length_adequacy_score": round(length_adequacy_score, 1),
            "pace_score": round(pace_score, 1),
            "sentence_len_score": round(sentence_len_score, 1),
        },
    )


def upsert_speech_summary(db: Session, sel_id: int, score: SpeechScoreResult) -> SpeechScoreSummary:
    row = db.query(SpeechScoreSummary).filter(SpeechScoreSummary.sel_id == sel_id).first()
    if row is None:
        row = SpeechScoreSummary(
            sel_id=sel_id,
            sss_fluency_score=score.fluency_score,
            sss_clarity_score=score.clarity_score,
            sss_structure_score=score.structure_score,
            sss_length_score=score.length_score,
        )
        db.add(row)
    else:
        row.sss_fluency_score = score.fluency_score
        row.sss_clarity_score = score.clarity_score
        row.sss_structure_score = score.structure_score
        row.sss_length_score = score.length_score
    db.commit()
    db.refresh(row)
    return row
