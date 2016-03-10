from distutils.core import setup
from setuptools import find_packages

import os


# Find all packages
PACKAGES = find_packages()

# Platform independent recovery of the home directory. It is always put as
# a hidden folder, '.noteorganiser', in the unix tradition.
MAIN = os.path.join(os.path.expanduser("~"), '.noteorganiser')

# Recover the data files, and place them
ASSET_FOLDER = os.path.join('noteorganiser', 'assets')
STYLE_FOLDER = os.path.join(ASSET_FOLDER, 'style')
ASSETS = [('', ['VERSION']),
          (MAIN,
           [os.path.join('example', 'example.md')]),
          (ASSET_FOLDER,
           [os.path.join(ASSET_FOLDER, 'notebook-128.png'),
            os.path.join(ASSET_FOLDER, 'folder-128.png')]),
          (STYLE_FOLDER,
           [os.path.join(STYLE_FOLDER, 'default.css'),
            os.path.join(STYLE_FOLDER, 'bootstrap.css'),
            os.path.join(STYLE_FOLDER, 'bootstrap-blog.html')]), ]

setup(name='NoteOrganiser',
      version=open('VERSION').read().strip(),
      description='Note Organiser for Scientists',
      long_description=open('README.md').read(),
      author='Benjamin Audren',
      author_email='benjamin.audren@gmail.com',
      license='MIT',
      url='https://github.com/baudren/NoteOrganiser',
      packages=PACKAGES,
      scripts=['noteorganiser/NoteOrganiser.py'],
      install_requires=['pypandoc', 'six', 'PySide>=1.2.2', 'qtawesome',
                        'qtpy<=0.1.3', 'pygments'],
      data_files=ASSETS,
      )
