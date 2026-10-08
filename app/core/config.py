from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENVIRONMENT: str

    class Config:
        env_file = ".env"

settings = Settings()