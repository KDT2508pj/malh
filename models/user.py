from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql import text

from .base import Base


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_username = Column(String(100), nullable=False)
    user_pw = Column(String(200), nullable=False)
    user_status = Column(
        Integer,
        nullable=False,
        server_default=text("1"),
        comment="1: user, 0: leaver",
    )

    # relationships
    resumes = relationship("Resume", back_populates="user")
    interview_sessions = relationship("InterviewSession", back_populates="user")
