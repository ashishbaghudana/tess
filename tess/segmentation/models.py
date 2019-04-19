from .textsplit import TextSplitSegmentationModel
from .pdfact import PdfActSegmentationModel
from pathlib import Path


def segmentation_dispatch(document):
    if document.algorithm == 'textsplit':
        model = TextSplitSegmentationModel(segment_strategy=document.segment_strategy,
                                           segment_length=document.num_splits)
        text = Path(document.document_path).read_text().strip()
        segments = model.segment(text)
        document.segments = segments
        document.status = 'DONE'
    elif document.algorithm == 'pdfact':
        model = PdfActSegmentationModel(unit=document.unit, format=document.format)
        segments = model.segment(document.document_path)
        document.segments = segments
        document.status = 'DONE'
    else:
        document.status = 'ERROR'
        document.segments = []
    document.save()
