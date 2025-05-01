from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

class Video(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    video_id: str = Field(length=11)
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    publish_time: str = Field(..., min_length=1)

    @validator('video_id')
    def video_id_validator(cls, v):
        if len(v) != 11:
            raise ValueError('Video ID must be exactly 11 characters long')
        return v


    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("video_id", 1)],
                "name": "video_id_index_1",
                "unique": True
            },
        ]