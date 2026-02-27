from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Text, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.sql import text

from .base import Base


class Question(Base):
    __tablename__ = "question"

    qust_id = Column(Integer, primary_key=True, autoincrement=True)
    set_id = Column(Integer, ForeignKey("question_set.set_id"), nullable=False)
    qust_category = Column(
        Enum("TECH", "PROJECT", "BEHAVIOR", "CS", "ETC"),
        nullable=False,
        server_default=text("'ETC'"),
    )
    qust_difficulty = Column(
        Enum("EASY", "MEDIUM", "HARD"),
        nullable=False,
        server_default=text("'MEDIUM'"),
    )
    qust_question_text = Column(Text, nullable=False)
    qust_evidence = Column(JSON, nullable=False)
    qust_is_selected = Column(
        Integer,
        nullable=False,
        server_default=text("0"),
        comment="0: 비채택, 1: 채택",
    )
    qust_created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    question_set = relationship("QuestionSet", back_populates="questions")
    filter_results = relationship("QuestionFilterResult", back_populates="question")
    selected_questions = relationship("SelectQuestion", back_populates="question")
