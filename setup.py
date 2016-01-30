import codecs
import mamonsu
from os import path
import mamonsu.lib.platform as platform

if platform.WINDOWS:
    from cx_Freeze import setup, Executable
else:
    from setuptools import setup, find_packages


def long_description():
    filespath = path.dirname(path.realpath(__file__))
    with codecs.open(path.join(filespath, 'README.rst'), encoding='utf8') as f:
        return f.read()


def executables():
    if platform.WINDOWS:
        return [Executable('agent.py')]

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
            'mamonsu=mamonsu.lib.supervisor:start'
        ],
    },
    options={'build_exe': {'packages': ['mamonsu'], 'optimize': 0}},
    executables=executables(),
    zip_safe=True,
)
