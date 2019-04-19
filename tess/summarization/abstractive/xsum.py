from typing import List
from urllib.parse import urlencode

import requests

from tess.summarization.abstractive import AbstractiveSummarizationModel
from tess.utils.tokenizer import word_tokenize


class XSumSummarizationModel(AbstractiveSummarizationModel):
    def __init__(self):
        self.url = "http://bollin.inf.ed.ac.uk:5427/xsum?"

    def predict(self, text: str, **kwargs):
        args = {'text': text}
        url = self.url + urlencode(args)
        response = requests.get(url)
        return response.json()['ConvS2S'][0].replace("&nbsp;", " ")

    def predict_batch(self, texts: List[str], **kwargs):
        raise NotImplementedError()

    def text_preprocess(self, text):
        text = ' '.join(word_tokenize(text))
        return text.encode('ascii', errors='ignore').decode('ascii', errors='ignore')
