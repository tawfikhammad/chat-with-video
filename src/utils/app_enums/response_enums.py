from enum import Enum

class ResponseSignals(Enum):

    VIDEO_NOT_FOUND_ERROR = "video not found error"
    INSERT_INTO_VECTORDB_SUCCESS = "insert into vector db success"
    INSERT_INTO_VECTORDB_ERROR = "insert into vector db error"
    RAG_ANSWER_SUCCESS = "rag answer success"
    RAG_ANSWER_ERROR = "rag answer error"

    VECTORDB_SEARCH_SUCCESS = "vector db search success"
    VECTORDB_SEARCH_ERROR = "vector db search error"

    VECTORDB_COLLECTION_RETRIEVED = "vector db collection retrieved"

    UNSUPPORTED_LLM_PROVIDER = "unsupported llm provider"
    UNSUPPORTED_VDB_PROVIDER = "unsupported vdb provider"
