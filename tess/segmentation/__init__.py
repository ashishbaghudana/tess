from abc import ABC, abstractmethod
from typing import List


class SegmentationModel(ABC):
    @abstractmethod
    def segment(self, text: str) -> List[str]:
        pass


class SegmentationModelError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
