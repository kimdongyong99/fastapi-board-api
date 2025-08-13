from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    PROJECT_NAME: str = "FastAPI Board API"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
