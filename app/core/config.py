from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    PROJECT_NAME: str = "FastAPI Board API"
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
