from pathlib import Path

import click

from tess.pipeline import Pipeline
from tess.segmentation.models import TextSplitSegmentationModel
from tess.summarization.models import SummaRuNNerModel

SEGMENTATION_MODELS = {
    "textsplit": TextSplitSegmentationModel
}
SEGMENTATION_MODEL_CHOICES = click.Choice(list(SEGMENTATION_MODELS.keys()))

SUMMARIZATION_MODELS = {
    "summarunner": SummaRuNNerModel
}
SUMMARIZATION_MODEL_CHOICES = click.Choice(list(SUMMARIZATION_MODELS.keys()))


@click.command()
@click.argument("file")
@click.option("--segmentation_model", help="Name of the segmentation model", required=False,
              type=SEGMENTATION_MODEL_CHOICES)
@click.option("--summarization_model", help="Name of the summarization model", required=False,
              type=SUMMARIZATION_MODEL_CHOICES)
def run_pipeline(file, segmentation_model, summarization_model):
    texts = Path(file).read_text().strip()
    pipeline = Pipeline(segmenter=SEGMENTATION_MODELS[segmentation_model](),
                        summarizer=SUMMARIZATION_MODELS[summarization_model]())
    summaries = pipeline.run(texts)
    print('\n'.join(summaries))
