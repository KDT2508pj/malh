from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey, JSON, Text, String, DateTime
from sqlalchemy.sql import text

from .base import Base


class AnswerAnalysis(Base):
    __tablename__ = "answer_analysis"

    anal_id = Column(Integer, primary_key=True, autoincrement=True)
    sel_id = Column(
        Integer,
        ForeignKey("select_question.sel_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    anal_overall_score = Column(Integer, nullable=False, comment="총점")
    anal_relevance_score = Column(Integer, nullable=False, comment="질문-답변-맥락 적합")
    anal_coverage_score = Column(Integer, nullable=False, comment="질문이 요구하는 요소 적합")
    anal_specificity_score = Column(Integer, nullable=False, comment="구체성")
    anal_evidence_score = Column(Integer, nullable=False, comment="근거")
    anal_consistency_score = Column(Integer, nullable=False, comment="이력서 정합성")

    anal_weakness = Column(
        JSON,
        nullable=False,
        comment="빈 배열은 약점없음, RELEVANCE, COVERAGE, SPECIFICITY, EVIDENCE, CONSISTENCY",
    )

    anal_relevance_reason = Column(Text, nullable=True)
    anal_coverage_reason = Column(Text, nullable=True)
    anal_specificity_reason = Column(Text, nullable=True)
    anal_evidence_reason = Column(Text, nullable=True)
    anal_consistency_reason = Column(Text, nullable=True)

    anal_good_points = Column(
        JSON,
        nullable=True,
        comment='[{"title":"", "detail":"", "metric":"SPECIFICITY"}] 형태',
    )
    anal_improvement_points = Column(
        JSON,
        nullable=True,
        comment='[{"title":"", "detail":"", "metric":"COVERAGE"}] 형태',
    )

    anal_overall_comment = Column(Text, nullable=True)
    anal_revised_answer = Column(Text, nullable=True)
    anal_llm_model = Column(String(100), nullable=True)

    anal_created_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    anal_updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )

    select_question = relationship("SelectQuestion", back_populates="answer_analysis")