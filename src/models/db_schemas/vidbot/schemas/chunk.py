from .vidbot_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Index
import uuid
from pydantic import BaseModel

class Chunk(SQLAlchemyBase):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, nullable=False)
    chunk_video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False)

    video = relationship("videos", back_populates="chunks")

    __table_args__ = (
        Index("chunk_video_id_index_1", chunk_video_id, unique=False),
    )

class RetrievedDocument(BaseModel):
    text: str
    score: float

