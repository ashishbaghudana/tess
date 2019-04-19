import json
import os
import uuid

import mongoengine
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from tess.config import UPLOAD_FILES
from tess.server.models import SummarizationDocument

summarization_bp = Blueprint('summarization_api', __name__)


@summarization_bp.route('', methods=['GET', 'POST'])
def summarize():
    if request.method == 'POST':
        body = request.form.to_dict()
        if 'file' not in request.files:
            return jsonify({'error': 400, 'message': 'Must supply a file'}), 400
        if not allowed_file(request.files['file'].filename):
            return jsonify({'error': 400, 'message': 'The file must be .txt'}), 400
        if 'algorithm' not in body:
            return jsonify({'error': 400, 'message': 'Algorithm should be specified'}), 400

        file = request.files['file']
        filename = secure_filename(file.filename)
        renamed_file = f"{uuid.uuid4().hex}.{get_extension(filename)}"
        file.save(os.path.join(UPLOAD_FILES, renamed_file))

        doc = SummarizationDocument(document_path=os.path.join(UPLOAD_FILES, renamed_file), algorithm=body['algorithm'])

        if 'tokenized' in body and body['tokenized']:
            doc.tokenized = True
            with open(os.path.join(UPLOAD_FILES, renamed_file)) as f:
                doc.processed_text = f.read().strip()

        if 'tokenizer' in body:
            doc.tokenizer = body['tokenizer']

        if 'target' in request.files:
            target_summary = request.files['target'].stream.read().decode()
            doc.target_summary = target_summary

        doc.status = 'NEW'

        doc.save()

        return jsonify(json.loads(doc.to_json())), 201

    if request.method == 'GET':
        documents = []
        for doc in SummarizationDocument.objects():
            documents.append({'id': str(doc.id),
                              'status': doc.status,
                              'algorithm': doc.algorithm,
                              'created_at': doc.created_at
                             })
        return jsonify(documents)


@summarization_bp.route('/<doc_id>', methods=['GET'])
def get_summary(doc_id):
    try:
        document = SummarizationDocument.objects.get(pk=doc_id)
        return jsonify(json.loads(document.to_json()))
    except mongoengine.errors.DoesNotExist as _:
        return jsonify({'error': 400, 'message': 'ID does not exist'})
    except mongoengine.errors.ValidationError as _:
        return jsonify({'error': 400, 'message': 'ID is invalid format'})


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'txt'


def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()
