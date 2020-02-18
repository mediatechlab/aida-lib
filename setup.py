import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

setup(
    name='aidalib',
    version='0.2',
    packages=['aida'],
    install_requires=[],
    license='MIT',

    author='Giulio Bottari',
    author_email='giuliobottari@gmail.com',
    description='Aida is a language agnostic library for text generation.',
    long_description=(HERE / "README.md").read_text(),
    long_description_content_type="text/markdown",
    keywords='nlg natural-language-generation text-generation library',
    url='https://github.com/mediatechlab/aida-lib',
    project_urls={
        'Bus Tracker': 'https://github.com/mediatechlab/aida-lib/issues',
        'Documentation': 'https://github.com/mediatechlab/aida-lib/blob/master/README.md',
        'Source Code': 'https://github.com/mediatechlab/aida-lib'
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
    ],
)
