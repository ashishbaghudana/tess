from abc import ABC, abstractmethod
from typing import List


class SummarizationModel(ABC):
    @abstractmethod
    def predict(self, text: str, **kwargs) -> str:
        pass

    @abstractmethod
    def predict_batch(self, texts: List[str], **kwargs) -> List[str]:
        pass

    @abstractmethod
    def text_preprocess(self, text):
        pass


class SummarizationModelError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
