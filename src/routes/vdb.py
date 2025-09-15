from fastapi import APIRouter, Request, Body, status
from fastapi.responses import JSONResponse
from src.controllers import RAGController
from src.models import VideoModel, ChunkModel
from .schema import PushRequest, SearchRequest
from utils.app_enums import ResponseSignals
from utils.logging import get_logger

vdb_router = APIRouter()
logger = get_logger(__name__)

@vdb_router.post("/index")
async def index_video(request: Request, video_id: str, push_request: PushRequest):

    video_model = await VideoModel.get_instance(db_client=request.app.db_client)
    chunk_model = await ChunkModel.get_instance(db_client=request.app.db_client)

    video = await video_model.get_video_by_ID(video_id=video_id)
    if not video:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignals.VIDEO_NOT_FOUND_ERROR.value})
    
    rag_controller = RAGController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0

    while has_records:
        page_chunks = await chunk_model.get_video_chunks(video_id=video.id, page_no=page_no)
        if len(page_chunks):
            page_no += 1
        
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunks_ids =  list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)
        
        is_inserted = await rag_controller.index_into_vector_db(
            video=video,
            chunks=page_chunks,
            chunks_ids=chunks_ids,
            do_reset=push_request.do_reset,
        )

        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignals.INSERT_INTO_VECTORDB_ERROR.value})

        inserted_items_count += len(page_chunks)
        logger.info(f"Inserted {inserted_items_count} items so far...")
        
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignals.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_items_count": inserted_items_count
        }
    )

@vdb_router.get("/info")
async def get_video_index_info(request: Request, video_id: str):
    
    video_model = await VideoModel.get_instance(db_client=request.app.db_client)
    video = await video_model.get_video_by_ID(video_id=video_id)

    rag_controller = RAGController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    collection_info = await rag_controller.get_vector_db_collection_info(video= video)

    return JSONResponse(
        content={
            "signal": ResponseSignals.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info
        }
    )

@vdb_router.post("/search")
async def search_index(request: Request, video_id: str, search_request: SearchRequest):
    
    video_model = await VideoModel.get_instance(db_client=request.app.db_client)
    video = await video_model.get_video_by_ID(video_id=video_id)

    rag_controller = RAGController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    results = await rag_controller.search_vector_db_collection(
        video=video,
        text=search_request.text,
        limit=search_request.limit
    )

    if not results:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignals.VECTORDB_SEARCH_ERROR.value
                }
            )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignals.VECTORDB_SEARCH_SUCCESS.value,
            "results": [result.dict() for result in results]
        }
    )
