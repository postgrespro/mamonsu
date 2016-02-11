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
            modules=['setup_win32_service'],
            cmdline_style='pywin32'
        )
    ],
    console=[{'script': 'mamonsu.py'}],
    options={
        'py2exe': {
            'packages': ['mamonsu'],
            'bundle_files': 1,
        }
    }
)
