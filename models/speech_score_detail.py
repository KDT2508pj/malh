from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from .base import Base


class SpeechScoreDetail(Base):
    __tablename__ = "speech_score_detail"

    detail_id = Column(Integer, primary_key=True, autoincrement=True)
    sel_id = Column(
        Integer,
        ForeignKey("select_question.sel_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    ssd_payload_json = Column(Text, nullable=False)

    select_question = relationship("SelectQuestion", back_populates="speech_score_detail")
