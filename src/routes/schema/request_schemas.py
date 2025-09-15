from pydantic import Field
from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    video_url: str = Field(..., example="https://www.youtube.com/watch?v=dQw4w9WgXcQ")

class PushRequest(BaseModel):
    do_reset: Optional[int] = 0

class SearchRequest(BaseModel):
    text: str = Field(..., example="What is the main topic of the video?")
    limit: Optional[int] = 5