from tess.summarization.extractive.summarunner.summarunner import SummaRuNNerModel
from tess.summarization.abstractive.xsum import XSumSummarizationModel
from tess.summarization.abstractive.pointer_summarizer import PointerGeneratorSummarizationModel
from tess.utils.tokenizer import sent_tokenize, text_preprocess, word_tokenize
from tess.evaluation.rouge import rouge_para


def summarization_dispatch(document):
    if document.algorithm == 'summarunner':
        summarunner(document)
    elif document.algorithm == 'xsum':
        xsum(document)
    elif document.algorithm == 'pgn':
        pgn(document)
    else:
        document.status = 'ERROR'
    document.save()


def summarunner(document):
    model = SummaRuNNerModel()
    with open(document.document_path) as f:
        raw_text = f.read().strip()
    document.processed_text = model.text_preprocess(raw_text)
    summary = model.predict(text=document.processed_text, topk=document.topk)
    document.summary = summary
    if document.target_summary:
        rouge_score = rouge_para(summary, document.target_summary)
        document.rouge_scores.rouge_1 = rouge_score.get('ROUGE-1')
        document.rouge_scores.rouge_2 = rouge_score.get('ROUGE-2')
        document.rouge_scores.rouge_l = rouge_score.get('ROUGE-L', 0.0)
    document.status = 'DONE'


def xsum(document):
    model = XSumSummarizationModel()
    with open(document.document_path) as f:
        raw_text = f.read().strip()
    document.processed_text = model.text_preprocess(raw_text)
    summary = model.predict(text=document.processed_text)
    document.summary = summary
    if document.target_summary:
        rouge_score = rouge_para(summary, document.target_summary)
        document.rouge_scores.rouge_1 = rouge_score.get('ROUGE-1')
        document.rouge_scores.rouge_2 = rouge_score.get('ROUGE-2')
        document.rouge_scores.rouge_l = rouge_score.get('ROUGE-L', 0.0)
    document.status = 'DONE'


def pgn(document):
    model = PointerGeneratorSummarizationModel()
    with open(document.document_path) as f:
        raw_text = f.read().strip()
    document.processed_text = model.text_preprocess(raw_text)
    summary = model.predict(text=document.processed_text)
    document.summary = summary
    if document.target_summary:
        rouge_score = rouge_para(summary, document.target_summary)
        document.rouge_scores.rouge_1 = rouge_score.get('ROUGE-1')
        document.rouge_scores.rouge_2 = rouge_score.get('ROUGE-2')
        document.rouge_scores.rouge_l = rouge_score.get('ROUGE-L', 0.0)
    document.status = 'DONE'
