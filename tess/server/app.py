import json
import os

from flask import Flask

from tess.config import TESS_ROOT_DIRECTORY
from tess.server.apis.summarization_api import summarization_api
from tess.server.config import Config
from tess.server.jobqueue import SqliteQueue

if __name__ == "__main__":
    # Opening the configuration file.
    with open(os.path.join(TESS_ROOT_DIRECTORY, 'config.json')) as f:
        # Parsing the JSON configs.
        config = Config(json.load(f))

    # Initialize the task queue
    queue = SqliteQueue(config.task_queue)

    # Creating a new app
    app = Flask("tess-backend")

    # Registering our API
    app.register_blueprint(summarization_api, prefixes={'v1': '/v1'})

    # Running the server.
    app.run(host=config.host, port=config.port)
