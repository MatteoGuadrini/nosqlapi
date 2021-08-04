from setuptools import setup
import __info__

with open("README.md") as fh:
    long_description = fh.read()

setup(
    name='nosqlapi',
    version=__info__.__version__,
    packages=['nosqlapi', 'nosqlapi.kvdb', 'nosqlapi.docdb', 'nosqlapi.common', 'nosqlapi.graphdb',
              'nosqlapi.columndb'],
    url=__info__.__homepage__,
    license='GNU General Public License v3.0',
    author=__info__.__author__,
    author_email=__info__.__email__,
    maintainer=__info__.__author__,
    maintainer_email=__info__.__email__,
    description='nosqlapi is a library for building standard NOSQL python libraries.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent",
        ],
    python_requires='>=3.6'
)
