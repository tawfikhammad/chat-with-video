from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from controllers import RAGController
from models import VideoModel, ChunkModel
from .schema import SearchRequest, PushRequest
from utils.app_enums import ResponseSignals
from utils import logging

logger = logging.get_logger(__name__)

rag_router = APIRouter()

@rag_router.post("/collections/{video_id}/index")
async def index_video(request: Request, video_id: str, push_request: PushRequest):

    video_model = await VideoModel.get_instance(db_client=request.app.db_client)
    chunk_model = await ChunkModel.get_instance(db_client=request.app.db_client)

    video = await video_model.get_video(video_id=video_id)
    if not video:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignals.VIDEO_NOT_FOUND.value})
    
    rag_controller = RAGController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )
    collection_name = rag_controller.create_collection_name(video_id=video.video_id)
    await rag_controller.create_vdb_collection(
        video_id=video.video_id,
        embedding_size=request.app.embedding_client.embedding_size,
        do_reset=push_request.do_reset,
    )

    has_records = True
    page_no = 1
    inserted_items_count = 0

    while has_records:
        page_chunks = await chunk_model.get_video_chunks(video=video, page_no=page_no)
        if len(page_chunks):
            logger.info(f"Fetched {len(page_chunks)} chunks from database for page {page_no}")
            page_no += 1
        
        if not page_chunks or len(page_chunks) == 0:
            logger.info(f"No more chunks found for video {video.id} on page {page_no}")
            has_records = False
            break
        
        await rag_controller.index_into_vdb_collection(
            chunks=page_chunks,
            collection_name=collection_name,
        )
        inserted_items_count += len(page_chunks)
        logger.info(f"Inserted {inserted_items_count} items so far...")
        
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignals.VECTORDB_INSERT_SUCCESS.value,
            "inserted_items_count": inserted_items_count
        }
    )

@rag_router.post("/collections/{video_id}/search")
async def search(request: Request, video_id: str, search_request: SearchRequest):
    
    video_model = await VideoModel.get_instance(db_client=request.app.db_client)
    video = await video_model.get_video(video_id=video_id)
    if not video:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "signal": ResponseSignals.VIDEO_NOT_FOUND.value})   

    rag_controller = RAGController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    results = await rag_controller.search_query(
        video=video,
        query=search_request.query,
        limit=search_request.limit
    )
    if not results:
        return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "signal": ResponseSignals.VECTORDB_NO_RESULTS_FOUND.value
                }
            )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignals.VECTORDB_SEARCH_SUCCESS.value,
            "results": [result.dict() for result in results]
        }
    )

@rag_router.post("/collections/{video_id}/answer")
async def answer_rag(request: Request, video_id: str, search_request: SearchRequest):
    
    video_model = await VideoModel.get_instance(db_client=request.app.db_client)
    video = await video_model.get_video(video_id=video_id)

    rag_controller = RAGController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    answer, full_prompt = await rag_controller.answer_question(
        video=video,
        query=search_request.query,
        limit=search_request.limit,
    )

    if not answer:
        return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "signal": ResponseSignals.RAG_NO_ANSWER.value}
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignals.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
        }
    )