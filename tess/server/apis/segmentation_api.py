from vibora.blueprints import Blueprint
from vibora.request import Request
from vibora.responses import JsonResponse

segmentation_api = Blueprint()


@segmentation_api.route('/', methods=['GET', 'POST'])
async def segment(request: Request):
    return JsonResponse({'hello': 'world'})
