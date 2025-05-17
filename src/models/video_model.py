from .base_model import BaseModel
from utils.app_enums import DatabaseEnums
from .db_schemas import Video

import logging
logger = logging.getLogger('unicorn.errors')

class VideoModel(BaseModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DatabaseEnums.VIDEO_COLLECTION_NAME.value]

    @classmethod
    async def get_instance(cls, db_client: object):
        instance = cls(db_client=db_client)
        await instance.ensure_indexes()
        return instance

    async def ensure_indexes(self):
        all_indexes = await self.collection.index_information()
        for index in Video.get_indexes():
            if index["name"] not in all_indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"])
                
    async def create_video(self, video: Video):
        existing_video  = await self.get_video_by_VideoID(video.video_id)
        if existing_video :
            logger.warning(f"Video with ID {video.video_id} already exists in the database.")
            return existing_video 
        res = await self.collection.insert_one(video.dict(by_alias=True, exclude_unset=True))
        video.id = res.inserted_id
        return video
    
    async def get_video_by_ID(self, video_id: str):
        record = await self.collection.find_one({"video_id": video_id})
        if record is None:
            return None
        return Video(**record)
    
    async def delete_video_by_ID(self, video_id: str):
        result = await self.collection.delete_one({"video_id": video_id})
        return result.deleted_count
    
    async def get_all_videos(self, page: int=0, limit: int=10):
        """
        return all videos in the database with pagination support starting from page 0 with a limit of 10
        """
        cursor = self.collection.find().skip(page * limit).limit(limit)
        videos = []
        async for document in cursor:
            videos.append(Video(**document))
        return videos
