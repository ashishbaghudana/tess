import json
from typing import List

import numpy as np
import torch
from torch.autograd import Variable
from torch.utils.data import DataLoader
from tqdm import tqdm

import tess.summarization.extractive.summarunner.models as models
from tess.summarization import SummarizationModelError
from tess.summarization.extractive import ExtractiveSummarizationModel
from tess.summarization.extractive.summarunner.utils import Vocab, make_dataset
from tess.utils.pkg_utility import check_model, get_file
from tess.utils.timing_utility import timeit
from tess.utils.tokenizer import word_tokenize, sent_tokenize


class SummaRuNNerModel(ExtractiveSummarizationModel):
    MODEL_NAME = 'summarunner'
    MODEL_FILES = ['model.pt', 'embedding.npz', 'word2id.json']

    def __init__(self):
        # Check if model exists
        if not check_model(self.MODEL_NAME, self.MODEL_FILES):
            raise SummarizationModelError(
                "Did not find all model files for {}. Run python -m tess download {} to re-download the model".format(
                    self.MODEL_NAME, self.MODEL_NAME))

        self.use_gpu = torch.cuda.is_available()

        self.embed = torch.Tensor(np.load(get_file(self.MODEL_NAME, 'embedding.npz'))['embedding'])
        with open(get_file(self.MODEL_NAME, 'word2id.json')) as f:
            self.word2id = json.load(f)
        self.vocab = Vocab(self.word2id)

        if self.use_gpu:
            self.checkpoint = torch.load(get_file(self.MODEL_NAME, 'model.pt'))
        else:
            self.checkpoint = torch.load(get_file(self.MODEL_NAME, 'model.pt'),
                                         map_location=lambda storage, loc: storage)
            self.checkpoint['args'].device = None

        self.net = getattr(models, self.checkpoint['args'].model)(self.checkpoint['args'])
        self.net.load_state_dict(self.checkpoint['model'])
        if self.use_gpu:
            self.net.cuda()
        self.net.eval()

    def predict(self, text: str, topk: int = 3) -> str:
        test_dataset = make_dataset([text])
        return self._predict(test_dataset, topk)[0]

    def predict_batch(self, texts: List[str], topk: int = 3) -> List[str]:
        test_dataset = make_dataset(texts)
        return self._predict(test_dataset, topk)

    def _predict(self, test_dataset, topk: int) -> List[str]:
        test_iter = DataLoader(dataset=test_dataset,
                               batch_size=1,
                               shuffle=False)
        file_id = 1
        summaries = []
        for batch in tqdm(test_iter):
            features, _, _, doc_lens = self.vocab.make_features(batch)
            if self.use_gpu:
                probs = self.net(Variable(features).cuda(), doc_lens)
            else:
                probs = self.net(Variable(features), doc_lens)
            start = 0
            for doc_id, doc_len in enumerate(doc_lens):
                stop = start + doc_len
                if len(probs.size()) == 0:
                    prob = torch.tensor(probs.item())
                else:
                    prob = probs[start:stop]
                topk = min(topk, doc_len)
                topk_indices = prob.topk(topk)[1].cpu().data.numpy()
                if topk_indices.shape == ():
                    topk_indices = topk_indices.reshape(-1)
                topk_indices.sort()
                doc = batch['doc'][doc_id].split('\n')[:doc_len]
                hyp = [doc[index] for index in topk_indices]
                summaries.append('\n'.join(hyp))
                start = stop
                file_id = file_id + 1
        return summaries

    def text_preprocess(self, text):
        text = '\n'.join(sent_tokenize(' '.join(word_tokenize(text)), 'nltk'))
        return text.encode('ascii', errors='ignore').decode('ascii', errors='ignore')
