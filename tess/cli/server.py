import atexit
import json
import os

from apscheduler.schedulers.background import BackgroundScheduler

from tess.config import TESS_ROOT_DIRECTORY
from tess.segmentation.models import segmentation_dispatch
from tess.summarization.models import summarization_dispatch
from tess.pipeline.models import pipeline_dispatch
from tess.server.app import app
from tess.server.config import Config
from tess.server.models import SegmentationDocument, SummarizationDocument, PipelineDocument


def run_segmentation():
    documents = SegmentationDocument.objects.filter(status="NEW")

    for document in documents:
        document.status = 'PROCESSING'
        document.save()

    for document in documents:
        segmentation_dispatch(document)


def run_summarization():
    documents = SummarizationDocument.objects.filter(status="NEW")

    for document in documents:
        document.status = 'PROCESSING'
        document.save()

    for document in documents:
        summarization_dispatch(document)


def run_pipeline():
    documents = PipelineDocument.objects.filter(status="NEW")

    for document in documents:
        document.status = 'PROCESSING'
        document.save()

    for document in documents:
        pipeline_dispatch(document)


def run_server():
    # Opening the configuration file.
    with open(os.path.join(TESS_ROOT_DIRECTORY, 'config.json')) as f:
        # Parsing the JSON configs.
        config = Config(json.load(f))

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=run_segmentation, trigger="interval", seconds=60)
    scheduler.add_job(func=run_summarization, trigger="interval", seconds=60)
    scheduler.add_job(func=run_pipeline, trigger="interval", seconds=60)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

    # Running the server.
    app.run(host=config.host, port=config.port, debug=False)
