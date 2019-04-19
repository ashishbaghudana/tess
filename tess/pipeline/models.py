from pathlib import Path
from tess.segmentation.models import TextSplitSegmentationModel, PdfActSegmentationModel
from tess.summarization.models import SummaRuNNerModel, PointerGeneratorSummarizationModel, XSumSummarizationModel
from tess.server.models import PipelineSummarizationDocument
from tess.utils.tokenizer import sent_tokenize, text_preprocess, word_tokenize
from tess.evaluation.rouge import rouge_para


def segmentation_textsplit(document):
    model = TextSplitSegmentationModel(segment_strategy=document.segmentation.segment_strategy,
                                       segment_length=document.segmentation.num_splits)
    text = Path(document.document_path).read_text().strip()
    segments = model.segment(text)
    document.segmentation.segments = segments
    document.segmentation.status = 'DONE'
    return segments


def segmentation_pdfact(document):
    model = PdfActSegmentationModel(unit=document.segmentation.unit, format=document.segmentation.format)
    segments = model.segment(document.document_path)
    document.segmentation.segments = segments
    document.segmentation.status = 'DONE'
    return segments


def summarization_summarunner(document, all_segments):
    # Initialize model
    model = SummaRuNNerModel()

    # Gather all summaries
    all_summaries = []

    # Iterate through each segment to get summary
    for segment in document.segmentation.segments:
        processed_text = model.text_preprocess(segment)
        summary_doc = PipelineSummarizationDocument(text=segment,
                                                    processed_text=processed_text,
                                                    status='PROCESSING')
        document.summarization.documents.append(summary_doc)
        document.save()

        summary = model.predict(text=summary_doc.processed_text, topk=summary_doc.topk)
        summary_doc.summary = summary
        summary_doc.status = 'DONE'
        all_summaries.append(summary)
        document.save()

    # Set summarization status to complete
    document.summarization.status = 'DONE'
    document.save()

    all_segments = model.text_preprocess(all_segments)
    all_segment_summary = model.predict(all_segments, 5)
    document.summarization.summary_without_segmentation = all_segment_summary

    document.save()

    return all_summaries


def summarization_pgn(document, all_segments):
    model = PointerGeneratorSummarizationModel()
    all_summaries = []
    for segment in document.segmentation.segments:
        processed_text = model.text_preprocess(segment)
        summary_doc = PipelineSummarizationDocument(text=segment,
                                                    processed_text=processed_text,
                                                    status='PROCESSING')
        document.summarization.documents.append(summary_doc)
        document.save()
        i = 0
        while i < 3:
            i += 1
            try:
                summary = model.predict(text=summary_doc.processed_text, topk=summary_doc.topk)
                summary_doc.summary = summary
                summary_doc.status = 'DONE'
                all_summaries.append(summary)
                break
            except Exception:
                continue
        document.save()

    document.summarization.status = 'DONE'
    document.save()

    all_segments = model.text_preprocess(all_segments)
    all_segment_summary = model.predict(all_segments)
    document.summarization.summary_without_segmentation = all_segment_summary

    document.save()

    return all_summaries


def summarization_xsum(document, all_segments):
    model = XSumSummarizationModel()
    all_summaries = []
    for segment in document.segmentation.segments:
        processed_text = model.text_preprocess(segment)
        summary_doc = PipelineSummarizationDocument(text=segment,
                                                    processed_text=processed_text,
                                                    status='PROCESSING')
        document.summarization.documents.append(summary_doc)
        document.save()
        summary = model.predict(text=summary_doc.processed_text, topk=summary_doc.topk)
        summary_doc.summary = summary
        summary_doc.status = 'DONE'
        all_summaries.append(summary)
        document.save()

    document.summarization.status = 'DONE'
    document.save()

    all_segments = model.text_preprocess(all_segments)
    all_segment_summary = model.predict(all_segments)
    document.summarization.summary_without_segmentation = all_segment_summary

    document.save()

    return all_summaries


def do_evaluation(document):
    if document.summarization.target_summary:
        rouge_score_without_segmentation = rouge_para(document.summarization.summary_without_segmentation,
                                                      document.summarization.target_summary)
        document.summarization.rouge_scores_without_segmentation.rouge_1 = rouge_score_without_segmentation.get(
            'ROUGE-1')
        document.summarization.rouge_scores_without_segmentation.rouge_2 = rouge_score_without_segmentation.get(
            'ROUGE-2')
        document.summarization.rouge_scores_without_segmentation.rouge_l = rouge_score_without_segmentation.get(
            'ROUGE-L')

        rouge_score = rouge_para(document.summarization.summary, document.summarization.target_summary)
        document.summarization.rouge_scores.rouge_1 = rouge_score.get('ROUGE-1')
        document.summarization.rouge_scores.rouge_2 = rouge_score.get('ROUGE-2')
        document.summarization.rouge_scores.rouge_l = rouge_score.get('ROUGE-L', 0.0)


def pipeline_dispatch(document):
    if document.segmentation.algorithm not in {'pdfact', 'lapdftext', 'textsplit'}:
        document.status = 'ERROR'
        document.segmentation.status = 'ERROR'
        document.summarization.status = 'ERROR'
        document.save()
        return

    # Run segmentation
    if document.segmentation.algorithm == 'textsplit':
        segments = segmentation_textsplit(document)
    elif document.segmentation.algorithm == 'pdfact':
        segments = segmentation_pdfact(document)
    document.save()

    document.summarization.status = 'PROCESSING'
    document.save()

    # Gather all segments from the document as a single text document
    all_segments = ' '.join(segments)

    # Run summarization on each segment
    if document.summarization.algorithm == 'summarunner':
        all_summaries = summarization_summarunner(document, all_segments)
    elif document.summarization.algorithm == 'pgn':
        all_summaries = summarization_pgn(document, all_segments)
    elif document.summarization.algorithm == 'xsum':
        all_summaries = summarization_xsum(document, all_segments)
    else:
        document.status = 'ERROR'
        document.save()
        return

    # Resummarize the individual segments together
    if document.summarization.resummarization_algorithm == 'summarunner':
        model = SummaRuNNerModel()
        full_text = model.text_preprocess(' '.join(all_summaries))
        document.summarization.summary = model.predict(full_text, 5)
    elif document.summarization.resummarization_algorithm == 'xsum':
        model = XSumSummarizationModel()
        full_text = model.text_preprocess(' '.join(all_summaries))
        document.summarization.summary = model.predict(full_text)
    elif document.summarization.resummarization_algorithm == 'pgn':
        model = PointerGeneratorSummarizationModel()
        full_text = model.text_preprocess(' '.join(all_summaries))
        document.summarization.summary = model.predict(full_text)

    do_evaluation(document)

    document.summarization.status = 'DONE'
    document.status = 'DONE'
    document.save()
