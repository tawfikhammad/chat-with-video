from .base_controller import BaseController
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils import logging
logger = logging.get_logger(__name__)

class TextProcessor(BaseController):
    def __init__(self):
        super().__init__()

    async def transcript_chunks(self, transcript: list, chunk_size:int= 200, chunk_overlap:int= 50) -> List[str]:

        try:
            strings = []
            for item in transcript:
                strings.append(f"{item['start']}: {item['text']}")

            strings = '\n'.join(strings)

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                is_separator_regex=False,)

            chunks = text_splitter.create_documents([strings])

            logger.info(f"Created {len(chunks)} chunks from transcript")
            return [chunk.page_content for chunk in chunks]

        except Exception as e:
            logger.error(f"Error chunking transcript: {str(e)}")
            return None   