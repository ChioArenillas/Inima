from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    AEMET_API_KEY: str = ""
    DATABASE_URL: str = "sqlite:///./weather_data.db"

    class Config:
        env_file = ".env"

settings = Settings()