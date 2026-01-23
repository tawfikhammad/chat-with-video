from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from utils.app_config import get_settings, settings
from utils.app_enums import ResponseSignals
from utils import logging
from controllers import DataController, RAGController, TextProcessor
from .schema import ProcessRequest
from models import VideoModel, ChunkModel
from models.db_schemas import Video, Chunk

logger = logging.get_logger(__name__)

data_router = APIRouter()

@data_router.post("/data/upload_url")
async def upload_video(request:Request, process_request:ProcessRequest, settings:settings= Depends(get_settings)):

    data_controller = DataController(video_url=process_request.video_url)
    video_id = await data_controller.get_video_id()
    if not video_id:
        logger.error("Invalid video URL provided")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": ResponseSignals.INVALID_VIDEO_URL.value}
        )
    
    video_model = await VideoModel.get_instance(db_client=request.app.db_client)
    video = await video_model.get_video(video_id=video_id)
    if video:
        logger.warning(f"Video with ID {video_id} already exists in the database.")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "signal": ResponseSignals.VIDEO_ALREADY_EXISTS.value,
                "video_id": video.video_id,
            }
        )

    # if video does not exist, proceed to fetch metadata and transcript
    metadata = await data_controller.get_video_metadata(video_id=video_id)
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

    chunks_model = await ChunkModel.get_instance(db_client=request.app.db_client)
    await chunks_model.insert_chunks(chunks=chunks)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignals.VIDEO_PROCESSING_SUCCESS.value,
            "video_id": video.video_id,
            "num_chunks": len(chunks)
        }
    )

@data_router.get("/data/videos")
async def list_videos(request:Request):
    video_model = await VideoModel.get_instance(db_client=request.app.db_client)
    videos = await video_model.get_all_videos()

    if not videos or len(videos) == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignals.VIDEO_LIST_EMPTY.value,
                "videos": []
            }
        )
    
    serialized_videos = []
    for video in videos:
        serialized_videos.append({
            "video_id": video.video_id,
            "title": video.title,
            "author": video.author,
            "description": video.description,
            "publish_time": video.publish_time,
        })
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignals.VIDEO_LIST_FETCH_SUCCESS.value,
            "videos": serialized_videos
        }
    )

@data_router.get("/data/videos/{video_id}")
async def get_video_details(request:Request, video_id:str):
    video_model = await VideoModel.get_instance(db_client=request.app.db_client)
    video = await video_model.get_video(video_id=video_id)
    if not video:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignals.VIDEO_NOT_FOUND.value
            }
        )
    
    chunk_model = await ChunkModel.get_instance(db_client=request.app.db_client)

    chunks_count = 0
    has_records = True
    page_no = 1
    while has_records:
        page_chunks = await chunk_model.get_video_chunks(video=video, page_no=page_no)
        if page_chunks and len(page_chunks):
            chunks_count += len(page_chunks)
            page_no += 1
        
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignals.VIDEO_FETCH_SUCCESS.value,
            "video": {
                "video_id": video.video_id,
                "video_chunks_count": chunks_count,
                "title": video.title,
                "author": video.author,
                "description": video.description,
                "publish_time": video.publish_time,
            }
        }
    )

@data_router.delete("/data/delete_video/{video_id}")
async def delete_video(request:Request, video_id:str):
    chunk_model = await ChunkModel.get_instance(db_client=request.app.db_client)
    video_model = await VideoModel.get_instance(db_client=request.app.db_client)

    video = await video_model.get_video(video_id=video_id)
    if not video:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignals.VIDEO_NOT_FOUND.value
            }
        )

    await chunk_model.del_video_chunks(video)
    await video_model.delete_video(video_id)
    
    rag_controller = RAGController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )
    await rag_controller.reset_vdb_collection(video_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignals.VIDEO_DELETE_SUCCESS.value,
        }
    )