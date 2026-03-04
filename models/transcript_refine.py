from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.sql import text

from .base import Base


class TranscriptRefine(Base):
    __tablename__ = "transcript_refine"

    r_refine_id = Column(Integer, primary_key=True, autoincrement=True)
    r_sel_id = Column(Integer, ForeignKey("select_question.sel_id"), nullable=False, unique=True)
    r_raw_text = Column(Text, nullable=False)
    r_refined_text = Column(Text, nullable=True)
    r_edit_log = Column(JSON, nullable=True)
    r_refine_confidence = Column(Integer, nullable=True, comment="0~100")
    r_changed_ratio = Column(Integer, nullable=True, comment="0~100")
    r_status = Column(String(20), nullable=False, server_default=text("'PENDING'"))
    r_reject_reason = Column(String(255), nullable=True)
    r_llm_model = Column(String(100), nullable=True)
    r_created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    r_updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )
