from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension
import numpy as np
import nltk

ext_modules=[
    Extension("*",
              ["dominance/*.pyx"],
            extra_compile_args = ["-O3", "-ffast-math", "-march=native"],
              )
]

with open("requirements.txt", "r") as req:
    requires = [row for row in req]

setup(
    name = "rfd-discovery",
    version = "0.0.1",
    #install_requires = requires,
    ext_modules= cythonize(ext_modules),
    include_dirs=[np.get_include()]
)

nltk.download('wordnet')
