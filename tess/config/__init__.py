import os

TESS_ROOT_DIRECTORY = os.path.join(os.path.expanduser('~'), '.tess')

PDFACT_JAR = os.path.join(TESS_ROOT_DIRECTORY, 'pdfact', 'pdfact.jar')

UPLOAD_FILES = os.path.join(TESS_ROOT_DIRECTORY, 'uploads')

ALLOWED_EXTENSIONS = {'txt', 'pdf'}
