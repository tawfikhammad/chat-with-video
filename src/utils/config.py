from pydantic_settings import BaseSettings

class settings(BaseSettings):

    APP_NAME: str 
    APP_VERSION: str 

    class Config:
        env_file = "src/.env"

def get_settings() -> settings:
    return settings()
