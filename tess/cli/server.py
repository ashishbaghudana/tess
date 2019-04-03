import json
import os

from vibora import Vibora

from tess.config import TESS_ROOT_DIRECTORY
from tess.server.apis import summarization_api
from tess.server.config import Config
from tess.server.jobqueue import TinyDBQueue
from tess.utils import BackgroundFunction
from tess.cli.predict import MODELS, MODEL_CHOICES


def run_predictions():
    queue = TinyDBQueue()
    for doc in queue.get_new():
        model = MODELS.get(doc["algorithm"], None)
        if model is None:
            continue
        doc["status"] = "PROCESSING"
        queue.update(doc.doc_id, doc)
        model = model()
        summary = model.predict(doc["text"])
        doc["summary"] = summary
        doc["status"] = "COMPLETE"
        queue.update(doc.doc_id, doc)


def run_server():
    # Opening the configuration file.
    with open(os.path.join(TESS_ROOT_DIRECTORY, 'config.json')) as f:
        # Parsing the JSON configs.
        config = Config(json.load(f))

    # Initialize the task queue
    queue = TinyDBQueue(config.task_queue, config.tables['task_queue'])
    print("Initialized queue: {} new elements".format(len(queue.get_new())))

    # Run the predictions function in the background
    bg_func = BackgroundFunction(run_predictions, interval=60)
    bg_func.run()

    # Creating a new app
    app = Vibora()

    # Registering the config as a component so you can use it
    # later on (as we do in the "before_server_start" hook)
    app.components.add(config)

    # Registering our API
    app.add_blueprint(summarization_api, prefixes={'v1/summarization': '/v1/summarization'})

    # Running the server.
    app.run(host=config.host, port=config.port)
