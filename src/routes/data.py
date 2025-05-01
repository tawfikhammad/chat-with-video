from fastapi import APIRouter, Depends, status, Request
from utils.app_config import get_settings, settings
from controllers import DataController, TextProcessor
from .schema import ProcessRequest
from models import VideoModel, ChunkModel
from models.db_schemas import Video, Chunk

import logging
logger = logging.getLogger('unicorn.errors')


data_router = APIRouter()

@data_router.post("/data/upload_url")
async def get_data(request:Request, process_request:ProcessRequest, settings:settings= Depends(get_settings)):

    if not process_request.video_url:
        logger.error("No video URL provided")
        return status.HTTP_400_BAD_REQUEST
    
    data_controller = DataController(video_url=process_request.video_url)
    is_valid, video_id = data_controller.get_video_id()

    if not is_valid:
        logger.error("Invalid video URL provided")
        return status.HTTP_400_BAD_REQUEST
    
    metadata = data_controller.get_video_metadata(video_id=video_id)

    try: 
        video_model = await VideoModel.get_instance(db_client=request.app.mongodb_client)
        video = await video_model.create_video(
            video=Video(
                video_id=video_id,
                title=metadata["title"],
                author=metadata["author"],
                description=metadata["description"],
                publish_time=metadata["publish_time"],
            )
        )
    except Exception as e:
        logger.error(f"Error creating video: {e}")
        return status.HTTP_500_INTERNAL_SERVER_ERROR


    transcript = data_controller.get_video_transcript(video_id=video_id)
    if not transcript:
        logger.error("No transcript found")
        return status.HTTP_400_BAD_REQUEST

    text_processor = TextProcessor()
    chunks = text_processor.transcript_chunks(transcript=transcript)

    chunks_model = await ChunkModel.get_instance(db_client=request.app.mongodb_client)
    try:
        await chunks_model.insert_chunks(chunks=chunks)
    except Exception as e:
        logger.error(f"Error inserting chunks: {e}")
        return status.HTTP_500_INTERNAL_SERVER_ERROR


    return metadata