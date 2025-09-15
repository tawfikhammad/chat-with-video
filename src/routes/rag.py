from fastapi import APIRouter, Request, Body, status
from fastapi.responses import JSONResponse
from controllers import RAGController
from models import VideoModel
from .schema import SearchRequest
from utils.app_enums import ResponseSignals
from utils.logging import get_logger

rag_router = APIRouter()
logger = get_logger(__name__)


@rag_router.post("/answer")
async def answer_rag(request: Request, video_id: str, search_request: SearchRequest):
    
    video_model = await VideoModel.get_instance(db_client=request.app.mongodb_client)
    video = await video_model.get_video_by_ID(video_id=video_id)

    rag_controller = RAGController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    answer, full_prompt = await rag_controller.answer_rag_question(
        video=video,
        query=search_request.text,
        limit=search_request.limit,
    )

    if not answer:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignals.RAG_ANSWER_ERROR.value}
        )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignals.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
        }
    )
