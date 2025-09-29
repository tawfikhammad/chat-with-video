from .base_model import BaseModel
from utils.app_enums import DatabaseEnums
from .db_schemas import Chunk, Video
from bson import ObjectId
from pymongo import InsertOne
from typing import List
from utils.logging import get_logger
logger = get_logger(__name__)

class ChunkModel(BaseModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DatabaseEnums.CHUNK_COLLECTION_NAME.value]

    @classmethod
    async def get_instance(cls, db_client):
        instance = cls(db_client)
        await instance.ensure_indexes()
        return instance
    
    async def ensure_indexes(self):
        all_indexes = await self.collection.index_information()
        for index in Chunk.get_indexes():
            if index["name"] not in all_indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"])

    async def create_chunk(self, chunk: Chunk):
        res = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))
        chunk.id = res.inserted_id
        return chunk

    async def get_chunk(self, chunk_id: ObjectId):
        record = await self.collection.find_one({"_id": chunk_id})
        if record is None:
            return None
        return Chunk(**record)

    async def insert_chunks(self, chunks: List[Chunk], batch_size:int=100):
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i: i+batch_size]  
            operation= [InsertOne(chunk.dict(by_alias=True, exclude_unset=True)) for chunk in batch]
            await self.collection.bulk_write(operation)
        return len(chunks)

    async def del_video_chunks(self, video_id: ObjectId):
        result = await self.collection.delete_many({"chunk_Video_id": video_id})
        return result.deleted_count
    
    async def get_video_chunks(self, video_id: ObjectId, page_no: int = 1, limit: int = 10) -> List[Chunk]:
        try:
            skip = (page_no - 1) * limit
            cursor = self.collection.find({"chunk_video_id": video_id}).skip(skip).limit(limit)
            docs = await cursor.to_list(length=limit)
            return [Chunk(**doc) for doc in docs]
        except Exception as e:
            logger.error(f"Error fetching video chunks for video ID {video_id}: {e}")
            return []

