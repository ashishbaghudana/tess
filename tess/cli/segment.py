from pathlib import Path

import click

from tess.segmentation.models import TextSplitSegmentationModel

SEGMENTATION_MODELS = {
    "textsplit": TextSplitSegmentationModel
}
SEGMENTATION_MODEL_CHOICES = click.Choice(list(SEGMENTATION_MODELS.keys()))


@click.command()
@click.argument("file")
@click.option("-m", "--segmentation_model", help="Name of the model", required=True,
              type=SEGMENTATION_MODEL_CHOICES)
def segment(file, segmentation_model):
    text = Path(file).read_text()
    segmenter = SEGMENTATION_MODELS[segmentation_model]()
    segmented_text = segmenter.segment(text)
    print(segmented_text)
