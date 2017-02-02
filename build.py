from distutils.core import setup
from distutils.extension import Extension
import numpy as np
from Cython.Build import cythonize

ext_modules=[
    Extension("*",
              ["dominance/*.pyx"],
              extra_compile_args = ["-O3", "-ffast-math", "-march=native"],
              )
]

setup(
    name = "rfd-discovery",
    version = "0.0.1",
    ext_modules= cythonize(ext_modules),
    include_dirs=[np.get_include()]
)
