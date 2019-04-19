from pathlib import Path

import click

from tess.summarization.models import SummaRuNNerModel, XSumSummarizationModel, PointerGeneratorSummarizationModel

MODELS = {
    "summarunner": SummaRuNNerModel,
    "xsum": XSumSummarizationModel,
    "pgn": PointerGeneratorSummarizationModel
}
MODEL_CHOICES = click.Choice(list(MODELS.keys()))


@click.command()
@click.argument("file")
@click.option("-m", "--model", help="Name of the model", required=True, type=MODEL_CHOICES)
@click.option("--topk", help="Select from top k choices", required=False, type=int, default=3)
def summarize(file, model, topk):
    text = Path(file).read_text()
    model_instance = MODELS[model]()
    summary = model_instance.predict(text, topk=topk)
    print(summary)
