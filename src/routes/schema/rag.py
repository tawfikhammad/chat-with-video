from pydantic import BaseModel
from pydantic import Field
from typing import Optional

class PushRequest(BaseModel):
    do_reset: Optional[int] = 0

class SearchRequest(BaseModel):
    text: str = Field(..., example="What is the main topic of the video?")
    limit: Optional[int] = 5