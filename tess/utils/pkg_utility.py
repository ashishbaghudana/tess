import os

from tess.config import TESS_ROOT_DIRECTORY


def check_model(model_name, model_files):
    """Check existence of downloaded model
    model_name (unicode): Name of the model
    model_files (list[unicode]): List of files associated with the model
    RETURNS (bool): True if all files exist, False otherwise
    """
    return all(
        [os.path.isfile(os.path.join(TESS_ROOT_DIRECTORY, model_name, model_file)) for model_file in model_files])


def get_file(model_name, file_name):
    """Return a file from the tess configuration directory
    model_name (unicode): Name of the model
    file_name (unicode): Name of the file to fetch
    RETURNS (unicode): Absolute path to file
    """
    return os.path.join(TESS_ROOT_DIRECTORY, model_name, file_name)
