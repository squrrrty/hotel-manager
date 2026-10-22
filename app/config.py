import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PRODUCTION = os.getenv("APP_ENV", "development") == "production"
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    # Явно выбираем уже установленный psycopg2, независимо от версии SQLAlchemy.
    SQLALCHEMY_DATABASE_URI = (os.getenv("DATABASE_URL") or "").replace(
        "postgres://", "postgresql://", 1
    ).replace(
        "postgresql://", "postgresql+psycopg2://", 1
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = PRODUCTION
    REMEMBER_COOKIE_SECURE = PRODUCTION
    MAX_CONTENT_LENGTH = 1024 * 1024
