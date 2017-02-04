from distutils.core import setup
from distutils.extension import Extension
import numpy as np
from Cython.Build import cythonize, build_ext


ext_modules=[
    Extension("*",
              ["dominance/*.pyx"],
              extra_compile_args = ["-O3", "-ffast-math", "-march=native"],
              ),
    Extension("*",
              ["loader/levenshtein_wrapper.pyx"]
              )
]

setup(
    name = "rfd-discovery",
    version = "0.0.1",
    cmdclass = {"build_ext": build_ext},
    ext_modules= cythonize(ext_modules),
    include_dirs=[np.get_include()]
)
