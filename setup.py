from setuptools import setup
from Cython.Build import cythonize
import numpy as np
import nltk

with open("requirements.txt", "r") as req:
    requires = [row for row in req]

setup(
    name = "rfd-discovery",
    version = "0.0.1",
    install_requires = requires,
    #ext_modules=cythonize(["loader/*.pyx", "dominance/*.pyx"]),
    include_dirs=[np.get_include()]
)

nltk.download('wordnet')