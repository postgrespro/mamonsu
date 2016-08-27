import codecs
import mamonsu
from os import path
from setuptools import setup, find_packages


def long_description():
    filespath = path.dirname(path.realpath(__file__))
    with codecs.open(path.join(filespath, 'README.rst'), encoding='utf8') as f:
        return f.read()

setup(
    name='mamonsu',
    version=mamonsu.__version__,
    packages=find_packages(),
    description=mamonsu.__description__,
    long_description=long_description(),
    classifiers=mamonsu.__classifiers__,
    keywords=mamonsu.__keywords__,
    author=mamonsu.__author__,
    author_email=mamonsu.__author_email__,
    url=mamonsu.__url__,
    license=mamonsu.__licence__,
    entry_points={
        'console_scripts': [
            'mamonsu=mamonsu.lib.runner:start'
        ],
    },
    zip_safe=True,
)
