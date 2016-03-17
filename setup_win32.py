import mamonsu
from setuptools import find_packages, setup
import py2exe


class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.version = mamonsu.__version__
        self.company_name = 'Postgres Professional'

setup(
    name='mamonsu',
    version=mamonsu.__version__,
    packages=find_packages(),
    description=mamonsu.__description__,
    classifiers=mamonsu.__classifiers__,
    keywords=mamonsu.__keywords__,
    author=mamonsu.__author__,
    author_email=mamonsu.__author_email__,
    url=mamonsu.__url__,
    license=mamonsu.__licence__,
    service=[
        Target(
            name='mamonsu',
            description='Zabbix active agent',
            modules=['service_win32'],
            cmdline_style='pywin32'
        )
    ],
    console=[{'script': 'mamonsu.py'}],
    options={
        'py2exe': {
            'packages': [
                'mamonsu',
                'mamonsu.plugins',
                'mamonsu.plugins.windows',
                'mamonsu.plugins.pgsql'
            ],
            'bundle_files': 1,
            'dist_dir': 'dist',
            'xref': False,
            'skip_archive': False,
            'ascii': False,
            'compressed': 2,
            'optimize': 2
        },
    },
    zipfile=None
)
