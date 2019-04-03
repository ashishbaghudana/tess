import numpy as np
import torch
import torch.utils.data as data
from typing import List


class Vocab():
    def __init__(self, word2id):
        self.word2id = word2id
        self.id2word = {v: k for k, v in word2id.items()}
        assert len(self.word2id) == len(self.id2word)
        self.PAD_IDX = 0
        self.UNK_IDX = 1
        self.PAD_TOKEN = 'PAD_TOKEN'
        self.UNK_TOKEN = 'UNK_TOKEN'

    def __len__(self):
        return len(self.word2id)

    def i2w(self, idx):
        return self.id2word[idx]

    def w2i(self, w):
        if w in self.word2id:
            return self.word2id[w]
        else:
            return self.UNK_IDX

    def make_features(self, batch, sent_trunc=50, doc_trunc=100, split_token='\n'):
        sents_list, targets, doc_lens = [], [], []
        # trunc document
        for doc, label in zip(batch['doc'], batch['labels']):
            sents = doc.split(split_token)
            labels = label.split(split_token)
            labels = [int(l) for l in labels]
            max_sent_num = min(doc_trunc, len(sents))
            sents = sents[:max_sent_num]
            labels = labels[:max_sent_num]
            sents_list += sents
            targets += labels
            doc_lens.append(len(sents))
        # trunc or pad sent
        max_sent_len = 0
        batch_sents = []
        for sent in sents_list:
            words = sent.split()
            if len(words) > sent_trunc:
                words = words[:sent_trunc]
            max_sent_len = len(words) if len(words) > max_sent_len else max_sent_len
            batch_sents.append(words)

        features = []
        for sent in batch_sents:
            feature = [self.w2i(w) for w in sent] + [self.PAD_IDX for _ in range(max_sent_len - len(sent))]
            features.append(feature)

        features = torch.LongTensor(features)
        targets = torch.LongTensor(targets)
        summaries = batch['summaries']

        return features, targets, summaries, doc_lens


class Dataset(data.Dataset):
    def __init__(self, examples):
        super(Dataset, self).__init__()
        self.examples = examples
        self.training = False

    def train(self):
        self.training = True
        return self

    def test(self):
        self.training = False
        return self

    def shuffle(self, words):
        np.random.shuffle(words)
        return ' '.join(words)

    def dropout(self, words, p=0.3):
        l = len(words)
        drop_index = np.random.choice(l, int(l * p))
        keep_words = [words[i] for i in range(l) if i not in drop_index]
        return ' '.join(keep_words)

    def __getitem__(self, idx):
        ex = self.examples[idx]
        return ex

    def __len__(self):
        return len(self.examples)


def make_dataset(texts: List[str]) -> Dataset:
    documents = []
    for text in texts:
        documents.append({
            "doc": text.strip(),
            "labels": "\n".join(["1" for _ in range(text.strip().count("\n") + 1)]),
            "summaries": ""
        })
    return Dataset(documents)
