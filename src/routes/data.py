from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from utils.app_config import get_settings, settings
from utils.app_enums import ResponseSignals
from utils import logging
from controllers import DataController, TextProcessor
from .schema import ProcessRequest
from models import VideoModel, ChunkModel
from models.db_schemas import Video, Chunk

logger = logging.get_logger(__name__)

data_router = APIRouter()

@data_router.post("/upload_url")
async def get_data(request:Request, process_request:ProcessRequest, settings:settings= Depends(get_settings)):

    data_controller = DataController(video_url=process_request.video_url)
    video_id = await data_controller.get_video_id()
    if not video_id:
        logger.error("Invalid video URL provided")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": ResponseSignals.INVALID_VIDEO_URL.value }
        )

    metadata = await data_controller.get_video_metadata(video_id=video_id)

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

    transcript = data_controller.get_video_transcript(video_id=video_id)
    if not transcript:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": ResponseSignals.TRANSCRIPT_NOT_FOUND.value}
        )

    text_processor = TextProcessor()
    processed_chunks = await text_processor.transcript_chunks(transcript=transcript)
    
    chunks = [
        Chunk(
            chunk_text=chunk_text,
            chunk_index=i,
            chunk_video_id=video.id
        ) for i, chunk_text in enumerate(processed_chunks)
    ]

    chunks_model = await ChunkModel.get_instance(db_client=request.app.mongodb_client)
    await chunks_model.insert_chunks(chunks=chunks)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignals.VIDEO_PROCESSING_SUCCESS.value,
            "num_chunks": len(chunks)
        }
    )