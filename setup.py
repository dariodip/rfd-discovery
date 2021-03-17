from setuptools import setup

"""Install the required packages and the lexical database WordNet"""

install_reqs = [line.strip() for line in open("requirements.txt") if not line.startswith('#')]

setup(
    name="rfd-discovery",
    version="0.0.1",
 #   install_requires=install_reqs,
    author="Dario Di Pasquale, Mattia Tomeo, Antonio Altamura",
    license="MIT",
)

import nltk
nltk.download('wordnet')
