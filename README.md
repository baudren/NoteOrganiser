Note Organiser for scientists
=============================


Objective
---------

Provide scientists, IT professionals but also normal people, with a solid,
lightweight note-taking GUI, with tag browsing and a clear interface.

Based on a customized markdown syntax, it supports mathematics. The
modification of the syntax, parsed internally, allows to store tags for posts,
for easier filtering when previewing a large document.

It is aimed to store small notes, remarks on program, life-pro-tips found while
developing/researching, in a safe place, reachable without internet access.

Eventually, it should also support longer posts (blog-like), and more
specialised types of notes, like ones for experimental work.

Installation
------------

Note Organiser uses the standard Python distutils tool for installing. Simply
issue:

    python setup.py install --user

when in the main directory. It requires PySide, and pypandoc, which you can
install with pip. **Be warned, PySide is a huge install**.

    pip install pypandoc --user
    pip install PySide --user

To get you started, look at the file `example/pyside.md`.

Usage
-----


Markdown
--------

For those still not familiar with Markdown, you can check the original code,
developed by John Gruber
[here](http://daringfireball.net/projects/markdown/syntax). It is a markup
language designed to be clear and readable, and easily converted to html for a
better visualisation.

Note Organiser converts notes taken in markdown with an additional syntax for
tags and date. The conversion is made through the python wrapper
[pypandoc](https://github.com/bebraw/pypandoc) of the
[pandoc](https://github.com/jgm/pandoc) document converter. The format will be
recognised automatically, and supports most extensions of markdown. A useful
cheat-sheet to consult is available [on this Github
wiki](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet).


Current Features
----------------

- Markdown syntax for a clear source file, readable without the software.
- Tag system for entries for classification
- Html previewing of the note file, with tag sorting

see the roadmap (display in raw format, since Github does not apply the Github
flavored syntax to files) for coming features, and make use of the issues page
to propose improvements.

License
-------

The code is published under the MIT license, please see LICENSE.txt for the
complete notice.
