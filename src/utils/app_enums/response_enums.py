from enum import Enum

class ResponseSignals(Enum):

    VIDEO_NOT_FOUND = "video not found in db"
    VIDEO_PROCESSING_SUCCESS = "video processing success"

    RAG_ANSWER_SUCCESS = "rag answer success"
    RAG_NO_ANSWER = "rag no answer found"

    VECTORDB_SEARCH_SUCCESS = "vector db search success"
    VECTORDB_NO_RESULTS_FOUND = "no results found from vector db search"
    VECTORDB_COLLECTION_RETRIEVED = "vector db collection retrieved"
    VECTORDB_INSERT_SUCCESS = "insert into vector db success"
    VECTORDB_INSERT_FAILED = "insert into vector db failed"

    UNSUPPORTED_LLM_PROVIDER = "unsupported llm provider"
    UNSUPPORTED_VDB_PROVIDER = "unsupported vdb provider"

    INVALID_VIDEO_URL = "invalid video url"
    TRANSCRIPT_NOT_FOUND = "transcript not found for video"