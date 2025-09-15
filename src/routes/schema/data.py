from pydantic_settings import BaseSettings
from pydantic import Field

class ProcessRequest(BaseSettings):
    video_url: str = Field(..., example="https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    