import sys
import textwrap
from pathlib import Path


def prints(*texts, **kwargs):
    """Print formatted message (manual ANSI escape sequences to avoid
    dependency)
    *texts (unicode): Texts to print. Each argument is rendered as paragraph.
    **kwargs: 'title' becomes coloured headline. exits=True performs sys exit.

    Adapted from https://github.com/explosion/spaCy/blob/master/spacy/print_utility.py
    """
    exits = kwargs.get('exits', None)
    title = kwargs.get('title', None)
    title = '\033[93m{}\033[0m\n'.format(_wrap(title)) if title else ''
    message = '\n\n'.join([_wrap(text) for text in texts])
    print('\n{}{}\n'.format(title, message))
    if exits is not None:
        sys.exit(exits)


def _wrap(text, wrap_max=80, indent=4):
    """Wrap text at given width using textwrap module.
    text (unicode): Text to wrap. If it's a Path, it's converted to string.
    wrap_max (int): Maximum line length (indent is deducted).
    indent (int): Number of spaces for indentation.
    RETURNS (unicode): Wrapped text.
    """
    indent = indent * ' '
    wrap_width = wrap_max - len(indent)
    if isinstance(text, Path):
        text = str(text)
    return textwrap.fill(text, width=wrap_width, initial_indent=indent,
                         subsequent_indent=indent, break_long_words=False,
                         break_on_hyphens=False)



