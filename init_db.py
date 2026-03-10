from core.database import engine
from models.base import Base
from sqlalchemy import text

from models.user import User
from models.resume import Resume
from models.resume_keyword import ResumeKeyword
from models.resume_classification import ResumeClassification
from models.resume_structured import ResumeStructured
from models.question_set import QuestionSet
from models.question import Question
from models.question_filter_result import QuestionFilterResult
from models.llm_run import LlmRun
from models.interview_session import InterviewSession
from models.select_question import SelectQuestion
from models.transcript import Transcript
from models.answer_analysis import AnswerAnalysis
from models.speech_score_summary import SpeechScoreSummary
from models.speech_score_detail import SpeechScoreDetail
from models.speech_feedback import SpeechFeedback
from models.audio_recording import AudioRecording


def main():
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

        Base.metadata.drop_all(bind=engine)
        print("🗑️ 기존 테이블 삭제 완료")

        Base.metadata.create_all(bind=engine)
        print("✅ 테이블 재생성 완료")

        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))


if __name__ == "__main__":
    main()
