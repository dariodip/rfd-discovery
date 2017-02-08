from distutils.core import setup
from distutils.extension import Extension
import numpy as np
from Cython.Build import cythonize, build_ext
import sys
"""
This module compile the Python code in format .pyx using Cython. It checks the platform used and uses
an appropriate compilation parameters.
"""
compiler_args_unix = ["-O3", "-ffast-math", "-march=native"]
compiler_args_vcpp = ["/O2", "/fp:fast", "/GL"]

platform = sys.platform

if platform.startswith('win'):
    compiler_args = compiler_args_vcpp
elif platform.startswith('darwin'):
    compiler_args = []
else:
    compiler_args = compiler_args_unix

ext_modules=[
    Extension("*",
              ["dominance/*.pyx"],
              extra_compile_args = compiler_args,
              ),
    Extension("*",
              ["loader/levenshtein_wrapper.pyx"],
              extra_compile_args = compiler_args,
              ),
    Extension("*",
              ["loader/distance_mtr.pyx"],
              extra_compile_args = compiler_args,
              )
]

setup(
    name = "rfd-discovery",
    version = "0.0.1",
    cmdclass = {"build_ext": build_ext},
    ext_modules= cythonize(ext_modules),
    include_dirs=[np.get_include()]
)
