from abc import ABC, abstractmethod

class LLMInterface(ABC):

    @abstractmethod
    def set_genration_model(self, genration_model_id: str ):
        pass

    @abstractmethod
    def set_embedding_model(self, embedding_model_id: str, embedding_size: int):
        pass

    @abstractmethod
    def generate(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                            temperature: float = None):
        pass

    @abstractmethod
    def embed(self, text: str):
        pass

    @abstractmethod
    def construct_prompt(self, prompt: str, role: str):
        pass
