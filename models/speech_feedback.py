from sqlalchemy import Column, ForeignKey, Integer, Text

from .base import Base


class SpeechFeedback(Base):
    __tablename__ = "speech_feedback"

    sfb_id = Column(Integer, primary_key=True, autoincrement=True)
    sel_id = Column(
        Integer,
        ForeignKey("select_question.sel_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    sfb_report_md = Column(Text, nullable=False)
    sfb_coaching_md = Column(Text, nullable=False)
    sfb_model = Column(Text, nullable=False)
