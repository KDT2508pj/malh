from typing import List, Literal

from pydantic import BaseModel, Field


MetricName = Literal["RELEVANCE", "COVERAGE", "SPECIFICITY", "EVIDENCE", "CONSISTENCY"]


class AnalysisPoint(BaseModel):
    title: str
    detail: str
    metric: MetricName


class AnswerAnalysisLLMResult(BaseModel):
    relevance_score: int = Field(ge=0, le=100)
    coverage_score: int = Field(ge=0, le=100)
    specificity_score: int = Field(ge=0, le=100)
    evidence_score: int = Field(ge=0, le=100)
    consistency_score: int = Field(ge=0, le=100)

    relevance_reason: str
    coverage_reason: str
    specificity_reason: str
    evidence_reason: str
    consistency_reason: str

    good_points: List[AnalysisPoint]
    improvement_points: List[AnalysisPoint]

    overall_comment: str
    revised_answer: str


def get_answer_analysis_response_format() -> dict:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "answer_analysis_result",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "relevance_score": {"type": "integer", "minimum": 0, "maximum": 100},
                    "coverage_score": {"type": "integer", "minimum": 0, "maximum": 100},
                    "specificity_score": {"type": "integer", "minimum": 0, "maximum": 100},
                    "evidence_score": {"type": "integer", "minimum": 0, "maximum": 100},
                    "consistency_score": {"type": "integer", "minimum": 0, "maximum": 100},
                    "relevance_reason": {"type": "string"},
                    "coverage_reason": {"type": "string"},
                    "specificity_reason": {"type": "string"},
                    "evidence_reason": {"type": "string"},
                    "consistency_reason": {"type": "string"},
                    "good_points": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "title": {"type": "string"},
                                "detail": {"type": "string"},
                                "metric": {
                                    "type": "string",
                                    "enum": ["RELEVANCE", "COVERAGE", "SPECIFICITY", "EVIDENCE", "CONSISTENCY"],
                                },
                            },
                            "required": ["title", "detail", "metric"],
                        },
                    },
                    "improvement_points": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "title": {"type": "string"},
                                "detail": {"type": "string"},
                                "metric": {
                                    "type": "string",
                                    "enum": ["RELEVANCE", "COVERAGE", "SPECIFICITY", "EVIDENCE", "CONSISTENCY"],
                                },
                            },
                            "required": ["title", "detail", "metric"],
                        },
                    },
                    "overall_comment": {"type": "string"},
                    "revised_answer": {"type": "string"},
                },
                "required": [
                    "relevance_score",
                    "coverage_score",
                    "specificity_score",
                    "evidence_score",
                    "consistency_score",
                    "relevance_reason",
                    "coverage_reason",
                    "specificity_reason",
                    "evidence_reason",
                    "consistency_reason",
                    "good_points",
                    "improvement_points",
                    "overall_comment",
                    "revised_answer",
                ],
            },
        },
    }