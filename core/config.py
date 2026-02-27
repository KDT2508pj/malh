from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

# repo 루트(mock-interview-ai/) 잡기: app/core/config.py 기준으로 2단계 위
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # 기본
    ENV: str = Field(default="dev")
    TZ: str = Field(default="Asia/Seoul")

    # ✅ Docker 없이도 바로 실행되게: 기본은 sqlite 로컬 파일 DB
    # (원하면 .env에서 MySQL URL로 덮어씀)
    DATABASE_URL: str = Field(
        default=f"sqlite+pysqlite:///{(PROJECT_ROOT / 'local.db').as_posix()}",
        description="dev 기본: sqlite. 운영: mysql+pymysql://... 로 덮어쓰기",
    )

    # 파일 저장
    STORAGE_DIR: str = Field(default=str(PROJECT_ROOT / "storage"))

    # LLM (선택)
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = Field(default="gpt-4.1-mini")

    # Celery/Redis (선택: Docker 없이 실행 시 비워도 됨)
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()