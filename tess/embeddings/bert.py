from flair.data import Sentence
from flair.embeddings import DocumentPoolEmbeddings, BertEmbeddings
import numpy as np


def get_sentence_embeddings(texts):
    word_embeddings = [BertEmbeddings('bert-large-uncased')]
    document_embeddings = DocumentPoolEmbeddings(word_embeddings)

    sentences = [Sentence(text) for text in texts]
    embeddings = []

    for sentence in sentences:
        document_embeddings.embed(sentence)
        sentence_embedding = sentence.get_embedding().numpy().reshape(-1)
        embeddings.append(sentence_embedding)

    return np.array(embeddings)
