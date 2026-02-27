from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey, JSON, DECIMAL

from .base import Base


class QuestionFilterResult(Base):
    __tablename__ = "question_filter_result"

    qfr_id = Column(Integer, primary_key=True, autoincrement=True)
    qust_id = Column(Integer, ForeignKey("question.qust_id"), nullable=False)
    qfr_reasons = Column(
        JSON,
        nullable=True,
        comment="MISSING_FIELD, INVALID_DIFFICULTY, EVIDENCE_EMPTY, DUPLICATE, CATEGORY_OVER_QUOTA, DIFFICULTY_OVER_QUOTA, TOO_SHORT, YESNO_OVER_QUOTA (복수가능 배열)",
    )
    qfr_duplicate_similarity = Column(
        DECIMAL(4, 3),
        nullable=True,
        comment="0.000 ~ 1.000, jaccard 규칙과 일치한지 체크 용도",
    )

    question = relationship("Question", back_populates="filter_results")
