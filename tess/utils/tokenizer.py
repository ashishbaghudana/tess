import sys

import nltk
import stanfordnlp


def text_preprocess(text):
    text = ' '.join(text.lower().split())
    return text


def sent_tokenize(text, model='newline'):
    partial = MODELS.get(model, nltk.sent_tokenize)
    return partial(text)


def newline_split_tokenize(text):
    return text.split('\n')


def stanfordnlp_tokenize(text):
    try:
        nlp = stanfordnlp.Pipeline()
        doc = nlp(text)
        return [' '.join([word.text for word in sentence.words]) for sentence in doc.sentences]
    except FileNotFoundError:
        print('StanfordNLP not installed. Run python -m tess download stanfordnlp to download models.', file=sys.stderr)
        return nltk.sent_tokenize(text)


def word_tokenize(text):
    return nltk.word_tokenize(text)


MODELS = {
    'nltk': nltk.sent_tokenize,
    'stanfordnlp': stanfordnlp_tokenize,
    'newline': newline_split_tokenize
}
