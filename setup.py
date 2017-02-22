from setuptools import setup
from pip.req import parse_requirements

"""Install the required packages and the lexical database WordNet"""

install_reqs = parse_requirements("requirements.txt", session='hack')
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name="rfd-discovery",
    version="0.0.1",
    install_requires=reqs,
    author="Dario Di Pasquale, Mattia Tomeo, Antonio Altamura",
    license="MIT",
)

import nltk
nltk.download('wordnet')
