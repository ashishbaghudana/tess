import json
import os

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install

with open('requirements.txt') as f:
    required = f.read().splitlines()


class PostDevelopCommand(develop):
    """Post-installation for development mode."""

    def run(self):
        directory = os.path.join(os.path.expanduser('~'), '.tess')
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, 'config.json'), 'w') as fw:
            json.dump({
                "host": "0.0.0.0",
                "port": 8000,
                "task_queue": os.path.join(directory, "db.json"),
                "tables": {
                    "task_queue": "task_queue"
                }
            }, fw)
        develop.run(self)


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        directory = os.path.join(os.path.expanduser('~'), '.tess')
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, 'config.json'), 'w') as fw:
            json.dump({
                "host": "0.0.0.0",
                "port": 8000,
                "task_queue": os.path.join(directory, "db.json"),
                "tables": {
                    "task_queue": "task_queue"
                }
            }, fw)
        install.run(self)


setup(
    name='tess-nlp',
    version='0.1.1',
    description='Text Extraction, Segmentation, and Summarization',
    url='http://github.com/ashishbaghudana/tess',
    author='Ashish Baghudana',
    author_email='ashish@ashishb.me',
    license='MIT',
    packages=['tess'],
    python_requires='>=3.6',
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
    zip_safe=False)
