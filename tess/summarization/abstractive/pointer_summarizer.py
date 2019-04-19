from typing import List

import requests

from tess.summarization.abstractive import AbstractiveSummarizationModel
from tess.utils.tokenizer import word_tokenize


class PointerGeneratorSummarizationModel(AbstractiveSummarizationModel):
    def __init__(self):
        self.url = "http://localhost:8090/"

    def predict(self, text: str, **kwargs):
        args = {'text': text}
        response = requests.post(self.url, json=args)
        return response.json()['summary']

    def predict_batch(self, texts: List[str], **kwargs):
        raise NotImplementedError()

    def text_preprocess(self, text):
        text = ' '.join(word_tokenize(text))
        return text.encode('ascii', errors='ignore').decode('ascii', errors='ignore')
