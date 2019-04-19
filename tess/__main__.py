import sys

from tess.cli import download, summarize, run_server, run_pipeline, segment
from tess.utils.print_utility import prints

if __name__ == '__main__':
    commands = {
        'download': download,
        'summarize': summarize,
        'server': run_server,
        'pipeline': run_pipeline,
        'segment': segment
    }
    if len(sys.argv) == 1:
        prints(', '.join(commands), title="Available commands", exits=1)
    command = sys.argv.pop(1)
    sys.argv[0] = 'tess %s' % command
    if command in commands:
        commands[command]()
    else:
        prints(
            "Available: %s" % ', '.join(commands),
            title="Unknown command: %s" % command,
            exits=1)
