import click

from tess.utils.print_utility import prints


@click.command()
@click.argument("model")
def download(model):
    if model in MODELS:
        prints("Downloading files for model %s..." % model)
        MODELS[model]()
    else:
        prints(
            "Available: %s" % ', '.join(MODELS),
            title="Unknown model: %s" % model,
            exits=1)


def download_stanfordnlp():
    import stanfordnlp
    stanfordnlp.download('en')


MODELS = {
    'stanfordnlp': download_stanfordnlp,
}
