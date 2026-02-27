from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.sql import text

from .base import Base


class ResumeKeyword(Base):
    __tablename__ = "resume_keyword"

    keyword_id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resume.resume_id"), nullable=False)
    llm_id = Column(Integer, ForeignKey("llm_run.llm_id"), nullable=False)
    keyword_keyword = Column(
        String(100),
        nullable=False,
        comment="Spring Boot 기반 REST API 설계 및 트랜잭션 처리 등",
    )
    keyword_type = Column(
        Enum(
            "SKILL","TOOL","DOMAIN_TERM","CERTIFICATE","ACHIEVEMENT","EDU","SOFT_SKILL","TASK","INDUSTRY","METRIC","ETC"
        ),
        nullable=False,
        server_default=text("'ETC'"),
    )
    keyword_evidence = Column(JSON, nullable=True)
    keyword_created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    resume = relationship("Resume", back_populates="keywords")
    llm_run = relationship("LlmRun", back_populates="resume_keywords")
