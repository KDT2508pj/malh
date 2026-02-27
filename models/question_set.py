from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.sql import text

from .base import Base


class QuestionSet(Base):
    __tablename__ = "question_set"

    set_id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resume.resume_id"), nullable=False)
    set_attempt = Column(
        Integer,
        nullable=True,
        server_default=text("1"),
        comment="1: 1회, 2: 2회",
    )
    set_status = Column(
        Enum("GENERATING", "FILTERING", "COMPLETED", "FAILED"),
        nullable=False,
        server_default=text("'GENERATING'"),
    )
    set_created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    set_updated_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    set_purpose = Column(
        Enum("DEFAULT", "WEAKNESS"),
        nullable=False,
        server_default=text("'DEFAULT'"),
    )

    resume = relationship("Resume", back_populates="question_sets")
    questions = relationship("Question", back_populates="question_set")
    interview_sessions = relationship("InterviewSession", back_populates="question_set")
