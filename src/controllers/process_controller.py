from .base_controller import BaseController
from langchain.text_splitter import RecursiveCharacterTextSplitter

class TextProcessor(BaseController):
    def __init__(self):
        super().__init__()

    def transcript_chunks(self, transcript: list, chunk_size:int= 500, chunk_overlap:int= 150) -> str:

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

            self.logger.info(f"Created {len(chunks)} chunks from transcript")
            return chunks 

        except Exception as e:
            self.logger.error(f"Error chunking transcript: {str(e)}")
            return None   