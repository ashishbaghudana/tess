import json
import os

from flask import Flask

from tess.config import TESS_ROOT_DIRECTORY, UPLOAD_FILES
from tess.server.blueprints import summarization_bp, segmentation_bp, pipeline_bp
from tess.server.config import Config
from tess.server.db import db

# Creating a new app
app = Flask("tess-backend")

# Registering our API
app.register_blueprint(segmentation_bp, url_prefix='/api/v1/segmentation')
app.register_blueprint(segmentation_bp, url_prefix='/api/v1/segmentation/')
app.register_blueprint(summarization_bp, url_prefix='/api/v1/summarization')
app.register_blueprint(summarization_bp, url_prefix='/api/v1/summarization/')
app.register_blueprint(pipeline_bp, url_prefix='/api/v1/pipeline')
app.register_blueprint(pipeline_bp, url_prefix='/api/v1/pipeline/')

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Database configuration in Flask App
app.config['MONGODB_SETTINGS'] = {
    'db': 'tess',
    'host': 'localhost',
    'port': 27017
}

os.makedirs(UPLOAD_FILES, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FILES

# Register DB to the app
db.init_app(app)


if __name__ == "__main__":
    # Opening the configuration file.
    with open(os.path.join(TESS_ROOT_DIRECTORY, 'config.json')) as f:
        # Parsing the JSON configs.
        config = Config(json.load(f))

    # Running the server.
    app.run(host=config.host, port=config.port, debug=True)
