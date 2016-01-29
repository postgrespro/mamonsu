import codecs
from setuptools import setup, find_packages
from mamonsu import __version__


def long_description():
    with codecs.open('README.rst', encoding='utf8') as f:
        return f.read()

setup(
    name='mamonsu',
    version=__version__,
    packages=find_packages(),
    description='Zabbix ative agent for monitoring PostgreSQL',
    long_description=long_description(),
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Monitoring'
    ],
    keywords=[
        'monitoring',
        'zabbix',
        'postgres'
    ],
    author='Dmitry Vasilyev',
    author_email='info@postgrespro.ru',
    url='https://github.com/postgrespro/mamonsu',
    license='BSD',
    entry_points={
        'console_scripts': [
            'mamonsu=mamonsu.lib.supervisor:start'
        ],
    },
    zip_safe=True,
)
