from distutils.core import setup
from setuptools import find_packages

import os

# Recover version from VERSION file
with open('VERSION', 'r') as version_file:
    VERSION = version_file.readline()

# Find all packages
PACKAGES = find_packages()

# Platform independent recovery of the home directory. It is always put as
# a hidden folder, '.noteorganiser', in the unix tradition.
MAIN = os.path.join(os.path.expanduser("~"), '.noteorganiser')

# Recover the data files, and place them
ASSETS = [('', ['VERSION']),
          (MAIN,
           ['example/example.md']),
          ('noteorganiser/assets/',
           ['noteorganiser/assets/notebook-128.png',
            'noteorganiser/assets/folder-128.png']),
          ('noteorganiser/assets/style',
           ['noteorganiser/assets/style/default.css']), ]

setup(name='NoteOrganiser',
      version=VERSION,
      description='Note Organiser for Scientists',
      author='Benjamin Audren',
      author_email='benjamin.audren@gmail.com',
      url='https://github.com/baudren/NoteOrganiser',
      packages=PACKAGES,
      scripts=['noteorganiser/NoteOrganiser.py'],
      install_requires=['pypandoc', 'PySide>=1.2.2', 'pygments'],
      data_files=ASSETS,
      )
