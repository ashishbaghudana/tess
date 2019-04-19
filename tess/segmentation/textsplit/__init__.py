from tess.embeddings.bert import get_sentence_embeddings
from tess.utils.tokenizer import sent_tokenize
from tess.segmentation import SegmentationModel
from .algorithm import split_greedy, split_optimal
from .tools import get_penalty, get_segments

DEFAULT_SEGMENT_LENGTH = 3


class TextSplitSegmentationModel(SegmentationModel):
    def __init__(self, segment_strategy='greedy', segment_length=30):
        self.segment_strategy = segment_strategy
        self.segment_length = segment_length
        self.segment_func = text_split

    def segment(self, text):
        return self.segment_func(text, self.segment_strategy, self.segment_length)


def text_split(text, algorithm='greedy', segment_length=30):
    if algorithm == 'greedy':
        return text_split_greedy(text, segment_length)
    elif algorithm == 'optimal':
        return text_split_optimal(text, segment_length)
    else:
        print(f'Invalid algorithm {algorithm} for text split. Defaulting to greedy.')
        return text_split_greedy(text, segment_length)


def text_split_optimal(text, segment_length=3):
    sentences = sent_tokenize(text.strip())
    sentence_embeddings = get_sentence_embeddings(sentences)
    penalty = get_penalty([sentence_embeddings], segment_length)
    optimal_segmentation = split_optimal(sentence_embeddings, penalty, seg_limit=250)
    segmented_text = get_segments(sentences, optimal_segmentation)
    segments = ['\n'.join(segment) for segment in segmented_text]
    return segments


def text_split_greedy(text, segment_length=3):
    sentences = sent_tokenize(text.strip())
    sentence_embeddings = get_sentence_embeddings(sentences)
    penalty = get_penalty([sentence_embeddings], segment_length)
    optimal_segmentation = split_greedy(sentence_embeddings, penalty)
    segmented_text = get_segments(sentences, optimal_segmentation)
    segments = ['\n'.join(segment) for segment in segmented_text]
    return segments
