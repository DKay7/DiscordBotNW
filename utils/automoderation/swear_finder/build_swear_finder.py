import os
import shutil
from distutils.core import setup
from Cython.Build import cythonize

from distutils.extension import Extension
extensions = [Extension(name='cython_swear_finder',
                        sources=['utils/automoderation/cython_swear_finder.pyx'])]

setup(name='cython bad words finder',
      ext_modules=cythonize(extensions)
      )

# os.remove(r"utils/automoderation/cython_swear_finder.c")
# shutil.rmtree(r"build")
