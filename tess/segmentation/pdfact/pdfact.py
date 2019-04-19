import json
import os
import subprocess
from tempfile import mkdtemp

from tess.config import PDFACT_JAR
from tess.segmentation import SegmentationModel, SegmentationModelError
from typing import List

DEFAULT_ROLES = ['body']


def _pdfact_split(path_to_pdf, unit='paragraphs', format='json', role=None):
    if role is None:
        role = DEFAULT_ROLES
    temp_dir = mkdtemp(prefix='tess-')
    basename = '.'.join(os.path.basename(path_to_pdf).split('.')[:-1])
    output_json = os.path.join(temp_dir, basename + '.json')
    output_visual_pdf = os.path.join(temp_dir, basename + '_visualized.pdf')

    input_command = ['java', '-jar', PDFACT_JAR, '--format', format, '--unit', unit, '--role', ' '.join(role),
                     '--visualize', output_visual_pdf, path_to_pdf, output_json]

    response = subprocess.run(input_command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    run_code = response.returncode

    response_content = {}
    if run_code == 0:
        with open(output_json) as f:
            response_content = json.load(f)
    return run_code, temp_dir, response_content


def pdfact_split(path_to_pdf, unit='paragraphs', format='json', role=None):
    run_code, temp_dir, response_content = _pdfact_split(path_to_pdf, unit, format, role)
    texts = []
    if 'document' in response_content:
        for doc in response_content['document']:
            texts.append(doc['paragraph']['text'])
    return run_code, texts


class PdfActSegmentationModel(SegmentationModel):
    def __init__(self, unit='paragraphs', format='json', role=None):
        self.unit = unit
        self.format = format
        self.role = role
        if not role:
            self.role = DEFAULT_ROLES

    def segment(self, path: str) -> List[str]:
        if not os.path.isfile(path):
            raise SegmentationModelError("The path provided must be a valid PDF")
        run_code, texts = pdfact_split(path, self.unit, self.format, self.role)
        return texts
