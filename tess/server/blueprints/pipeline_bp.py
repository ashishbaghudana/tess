import json
import os
import uuid

import mongoengine
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from tess.config import ALLOWED_EXTENSIONS, UPLOAD_FILES
from tess.server.models import (PipelineDocument, PipelineSummarizationCollection, PipelineSegmentationDocument)

pipeline_bp = Blueprint('pipeline_api', __name__)


@pipeline_bp.route('/<pipeline_id>', methods=['GET'])
def get_pipeline(pipeline_id):
    try:
        document = PipelineDocument.objects.get(pk=pipeline_id)
        return jsonify(json.loads(document.to_json()))
    except mongoengine.errors.DoesNotExist as _:
        return jsonify({'error': 400, 'message': 'ID does not exist'}), 400
    except mongoengine.errors.ValidationError as _:
        return jsonify({'error': 400, 'message': 'ID is invalid format'}), 400


@pipeline_bp.route('', methods=['GET', 'POST'])
def create_pipeline():
    if request.method == 'POST':
        body = request.form.to_dict()
        if 'segmentation_algorithm' not in body:
            return jsonify({'error': 400, 'message': 'Must supply segmentation algorithm'}), 400
        if 'segmentation_algorithm' not in body:
            return jsonify({'error': 400, 'message': 'Must supply summarization algorithm'}), 400
        if 'file' not in request.files:
            return jsonify({'error': 400, 'message': 'Must supply file for segmentation and summarization'}), 400

        file = request.files['file']
        if not allowed_file(file.filename):
            return jsonify({'error': 400, 'message': f'The extension must be one of {ALLOWED_EXTENSIONS}'}), 400

        filename = secure_filename(file.filename)
        renamed_file = f"{uuid.uuid4().hex}.{get_extension(filename)}"
        file.save(os.path.join(UPLOAD_FILES, renamed_file))

        segmentation_doc = PipelineSegmentationDocument(algorithm=body['segmentation_algorithm'], status='NEW')
        if 'segmentation_num_splits' in body:
            segmentation_doc.num_splits = body['segmentation_num_splits']
        if 'segmentation_format' in body:
            segmentation_doc.format = body['segmentation_format']
        if 'segmentation_unit' in body:
            segmentation_doc.role = body['unit']
        if 'segmentation_strategy' in body:
            segmentation_doc.segment_strategy = body['segmentation_strategy']

        summarization_col = PipelineSummarizationCollection(algorithm=body['summarization_algorithm'], status='NEW')
        if 'summarization_tokenizer' in body:
            summarization_col.tokenizer = body['summarization_tokenizer']
        if 'resummarization_algorithm' in body:
            summarization_col.resummarization_algorithm = body['resummarization_algorithm']
        if 'target' in request.files:
            target_summary = request.files['target'].stream.read().decode()
            summarization_col.target_summary = target_summary

        doc = PipelineDocument(document_path=os.path.join(UPLOAD_FILES, renamed_file),
                               segmentation=segmentation_doc,
                               summarization=summarization_col,
                               status='NEW')
        doc.save()

        return jsonify({"id": str(doc.id), "status": 'NEW'}), 201
    if request.method == 'GET':
        documents = []
        for doc in PipelineDocument.objects():
            documents.append({'id': str(doc.id),
                              'status': doc.status,
                              'segmentation': {'algorithm': doc.segmentation.algorithm},
                              'summarization': {
                                  'algorithm': doc.summarization.algorithm,
                                  'resummarization_algorithm': doc.summarization.resummarization_algorithm
                              },
                              'created_at': doc.created_at,
                              })
        documents.sort(key=lambda item: item['created_at'], reverse=False)
        return jsonify(documents)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()
