from distutils.core import setup
from setuptools import find_packages

# Recover version from VERSION file
with open('VERSION', 'r') as version_file:
    VERSION = version_file.readline()

PACKAGES = find_packages()

# Recover assets
ASSETS = [('', ['VERSION']),
          ('', ['example/pyside.md']),
          ('', ['noteorganiser/assets/notebook-128.png',
                'noteorganiser/assets/folder-128.png']),
          ('', ['noteorganiser/assets/style/default.css']), ]

setup(name='NoteOrganiser',
      version=VERSION,
      description='Note Organiser for Scientists',
      author='Benjamin Audren',
      author_email='benjamin.audren@gmail.com',
      url='https://github.com/baudren/NoteOrganiser',
      packages=PACKAGES,
      scripts=['noteorganiser/NoteOrganiser.py'],
      #install_requires=['pypandoc', 'PySide'],
      data_files=ASSETS,
      )
