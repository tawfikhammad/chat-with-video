from pydantic import BaseModel, Field
from typing import List, Optional
from bson.objectid import ObjectId

class Chunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_index: int = Field(..., ge=0)
    chunk_video_id: ObjectId
    
    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("chunk_video_id", 1)],
                "name": "chunk_video_id_index_1",
                "unique": False
            }
        ]
    
class RetrievedDocument(BaseModel):
    text: str
    score: float