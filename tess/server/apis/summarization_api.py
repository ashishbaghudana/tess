from jsonschema import ValidationError
from jsonschema import validate
from vibora.blueprints import Blueprint
from vibora.request import Request
from vibora.responses import JsonResponse

from tess.server.error_codes import INVALID_REQUEST, DOCUMENT_NOT_FOUND
from tess.server.jobqueue import TinyDBQueue
from tess.server.schemas import SUMMARIZATION_SCHEMA, SUMMARIZATION_ALGORITHMS
from tess.utils.date_utility import date_to_string


summarization_api = Blueprint()


@summarization_api.route('', methods=['POST'])
def summarize(request: Request):
    task_queue = TinyDBQueue()
    try:
        request_json = await(request.json())
        validate(request_json, SUMMARIZATION_SCHEMA)
        if request_json["algorithm"] not in SUMMARIZATION_ALGORITHMS[request_json["method"]]:
            raise ValidationError(
                "Algorithm {} does not match the type of method {} provided".format(request_json["algorithm"],
                                                                                    request_json["method"]))
        request_json['status'] = 'NEW'
        current_time = date_to_string()
        request_json['created'] = current_time
        id = task_queue.append(request_json)
        return JsonResponse({'id': id, 'created': current_time, 'status': 'NEW'}, status_code=201)
    except ValidationError as error:
        return JsonResponse({'message': error.message, 'code': INVALID_REQUEST}, status_code=400)


@summarization_api.route('/<doc_id>', methods=['GET'])
def summarize(doc_id: int):
    task_queue = TinyDBQueue()
    doc = task_queue.get(doc_id)
    if doc is None:
        return JsonResponse({'message': 'Document not found', 'code': DOCUMENT_NOT_FOUND}, status_code=404)
    return JsonResponse(doc)
