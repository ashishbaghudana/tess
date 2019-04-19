import json
import os
import uuid

import mongoengine
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from tess.config import ALLOWED_EXTENSIONS, UPLOAD_FILES
from tess.server.models import SegmentationDocument

segmentation_bp = Blueprint('segmentation_api', __name__)


@segmentation_bp.route('/<id>', methods=['GET'])
def get_segments(id):
    try:
        document = SegmentationDocument.objects.get(pk=id)
        return jsonify(json.loads(document.to_json()))
    except mongoengine.errors.DoesNotExist as _:
        return jsonify({'error': 400, 'message': 'ID does not exist'}), 400
    except mongoengine.errors.ValidationError as _:
        return jsonify({'error': 400, 'message': 'ID is invalid format'}), 400


@segmentation_bp.route('', methods=['POST', 'GET'])
def segment():
    if request.method == 'POST':
        body = request.form.to_dict()
        if 'algorithm' not in body:
            return jsonify({'error': '400', 'message': 'Must supply algorithm'}), 400
        if body['algorithm'] in {'pdfact', 'lapdftext'} and 'file' not in request.files:
            return (
                jsonify({'error': 400, 'message': 'If algorithm is "pdfact" or "lapdftext", a pdf file must be supplied'}),
                400)
        file = request.files['file']
        if not allowed_file(file.filename):
            return jsonify({'error': 400, 'message': f'The extension must be one of {ALLOWED_EXTENSIONS}'}), 400

        filename = secure_filename(file.filename)
        renamed_file = f"{uuid.uuid4().hex}.{get_extension(filename)}"
        file.save(os.path.join(UPLOAD_FILES, renamed_file))

        doc = SegmentationDocument(document_path=os.path.join(UPLOAD_FILES, renamed_file),
                                   algorithm=body.get('algorithm'),
                                   num_splits=body.get('num_splits', None),
                                   status='NEW')
        doc.save()
        return jsonify({"id": str(doc.id), "status": 'NEW'}), 201

    if request.method == 'GET':
        documents = []
        for doc in SegmentationDocument.objects():
            documents.append({'id': str(doc.id),
                              'status': doc.status,
                              'algorithm': doc.algorithm,
                             })
        return jsonify(documents)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_extension(filename):
    return filename.rsplit('.', 1)[1].lower()
