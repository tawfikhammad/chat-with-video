from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from utils.app_config import get_settings, settings
from utils.logging import get_logger
from controllers import DataController, TextProcessor
from .schema import ProcessRequest
from models import VideoModel, ChunkModel
from models.db_schemas import Video, Chunk

logger = get_logger(__name__)

data_router = APIRouter()

@data_router.post("/upload_url")
async def get_data(request:Request, process_request:ProcessRequest, settings:settings= Depends(get_settings)):

    try: 
        data_controller = DataController(video_url=process_request.video_url)
        video_id = data_controller.get_video_id()

        if not video_id:
            logger.error("Invalid video URL provided")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": "INVALID_VIDEO_URL"}
            )
    
        metadata = data_controller.get_video_metadata(video_id=video_id)

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
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": "TRANSCRIPT_FETCH_ERROR"}
            )

        text_processor = TextProcessor()
        chunks = text_processor.transcript_chunks(transcript=transcript)
        if not chunks:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": "TRANSCRIPT_CHUNKING_ERROR"}
            )

        chunks_model = await ChunkModel.get_instance(db_client=request.app.mongodb_client)
        await chunks_model.insert_chunks(chunks=chunks)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": "VIDEO_PROCESSING_SUCCESS",
                "video_id": str(video.id),
                "num_chunks": len(chunks)
            }
        )
    
    except Exception as e:
        logger.error(f"Error processing video URL: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"signal": "INTERNAL_SERVER_ERROR"} 
        )   