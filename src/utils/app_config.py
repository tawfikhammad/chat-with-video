from pydantic_settings import BaseSettings

class settings(BaseSettings):

    APP_NAME: str 
    APP_VERSION: str 
    YOUTUBE_API: str
    MONGO_URL: str
    MONGO_DB: str = "vidbot"

    class Config:
        env_file = "src/.env"

def get_settings() -> settings:
    return settings()
