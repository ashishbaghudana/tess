from typing import Union

from tess.segmentation import SegmentationModel
from tess.summarization import SummarizationModel


class Pipeline(object):
    def __init__(self, segmenter: Union[None, SegmentationModel] = None,
                 summarizer: Union[None, SummarizationModel] = None):
        self.segmenter = segmenter
        self.summarizer = summarizer

    def run(self, text):
        summaries = []

        if self.segmenter:
            segmented_texts = self.segmenter.segment(text)
        else:
            segmented_texts = [text]

        if self.summarizer:
            summarized_texts = self.summarizer.predict_batch(segmented_texts)
        else:
            summarized_texts = segmented_texts

        summaries.append(summarized_texts)

        return summaries
