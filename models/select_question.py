from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import text

from .base import Base


class SelectQuestion(Base):
    __tablename__ = "select_question"

    sel_id = Column(Integer, primary_key=True, autoincrement=True)
    inter_id = Column(Integer, ForeignKey("interview_session.inter_id"), nullable=False)
    qust_id = Column(Integer, ForeignKey("question.qust_id"), nullable=False)
    sel_order_no = Column(Integer, nullable=False, comment="1~5")
    sel_asked_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    sel_answer_duration_sec = Column(
        Integer,
        nullable=False,
        server_default=text("0"),
        comment="해당 질문 답변의 녹음 길이를 초 단위로 저장한 값",
    )

    interview_session = relationship("InterviewSession", back_populates="selected_questions")
    question = relationship("Question", back_populates="selected_questions")

    transcript = relationship("Transcript", back_populates="select_question", uselist=False)
    answer_analysis = relationship("AnswerAnalysis", back_populates="select_question", uselist=False)
    speech_summary = relationship("SpeechScoreSummary", back_populates="select_question", uselist=False)
