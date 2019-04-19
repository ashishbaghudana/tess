from tess.server.db import db
import mongoengine_goodjson as gj
from datetime import datetime


class RougeDocument(gj.EmbeddedDocument):
    rouge_1 = db.FloatField(default=0.0)
    rouge_2 = db.FloatField(default=0.0)
    rouge_l = db.FloatField(default=0.0)


class PipelineSegmentationDocument(gj.EmbeddedDocument):
    algorithm = db.StringField(max_length=30, required=True)
    num_splits = db.IntField(default=30)
    status = db.StringField(max_length=15, required=True)
    format = db.StringField(max_length=4, default='json')
    unit = db.StringField(default='paragraphs')
    segments = db.ListField(db.StringField())
    segment_strategy = db.StringField(default='greedy')


class PipelineSummarizationDocument(gj.EmbeddedDocument):
    text = db.StringField(required=True)
    processed_text = db.StringField(default='')
    status = db.StringField(max_length=15, required=True)
    topk = db.IntField(default=2)
    summary = db.StringField()


class PipelineSummarizationCollection(gj.EmbeddedDocument):
    tokenizer = db.StringField(default='nltk')
    status = db.StringField(max_length=15, required=True)
    documents = db.EmbeddedDocumentListField(PipelineSummarizationDocument, default=[])
    target_summary = db.StringField(default='')
    rouge_scores = db.EmbeddedDocumentField(RougeDocument, default=RougeDocument())
    algorithm = db.StringField(max_length=30, required=True)
    resummarization_algorithm = db.StringField(max_length=30, required=False, default='summarunner')
    summary_without_segmentation = db.StringField()
    rouge_scores_without_segmentation = db.EmbeddedDocumentField(RougeDocument, default=RougeDocument())
    summary = db.StringField()


class PipelineDocument(gj.Document):
    document_path = db.StringField(max_length=500)
    segmentation = db.EmbeddedDocumentField(PipelineSegmentationDocument, required=True)
    summarization = db.EmbeddedDocumentField(PipelineSummarizationCollection, required=True)
    created_at = db.DateTimeField(default=datetime.utcnow)
    status = db.StringField(max_length=15, required=True)


class SegmentationDocument(gj.Document):
    document_path = db.StringField(max_length=500, required=True)
    algorithm = db.StringField(max_length=30, required=True)
    num_splits = db.IntField(default=30)
    status = db.StringField(max_length=15, required=True)
    format = db.StringField(max_length=4, default='json')
    unit = db.StringField(default='paragraphs')
    segments = db.ListField(db.StringField())
    segment_strategy = db.StringField(default='greedy')
    created_at = db.DateTimeField(default=datetime.utcnow)


class SummarizationDocument(gj.Document):
    document_path = db.StringField(max_length=500, required=True)
    tokenizer = db.StringField(default='')
    tokenized = db.BooleanField(default=False)
    processed_text = db.StringField(default='')
    algorithm = db.StringField(max_length=30, required=True)
    topk = db.IntField(default=3)
    status = db.StringField(max_length=15, required=True)
    summary = db.StringField()
    target_summary = db.StringField(default='')
    rouge_scores = db.EmbeddedDocumentField(RougeDocument, default=RougeDocument())
    created_at = db.DateTimeField(default=datetime.utcnow)

