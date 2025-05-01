from pydantic_settings import BaseSettings

class ProcessRequest(BaseSettings):
    video_url: str = None

    