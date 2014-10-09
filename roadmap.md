Roadmap for 0.2
===============

# General
[~] Ensure compatibility with python 3 and 2
[.] Document more.
[ ] Improve keyboard shortcuts (ctrl instead of alt, etc).
[ ] Ensure proper resizing at all times.
[?] Ensure proper key navigation at all times (sometimes ctrl+tab does not
    switch between tabs)
[x] Keyboard shortcut for accessing the tabs
[x] Use py.test and qtbot module to test the individual functionalities.
    [x] replace calls to parent's methods by proper use of signal/slot
    [x] ensuring proper relative import for tests (for py27)
    [x] tests *actually* passing
    [x] using mock windows, and QTimer for popups
    [ ] testing the right-click menu on buttons?
[x] Use persistent settings to be stored, for window's size and position

# Library
[ ] draw vector icons, and use several sizes
[ ] variable number of columns/line on the shelves
[ ] resizing should change the number of columns/lines for the shelves
[ ] Display all tags in this zone
[x] Create folder
[ ] Display the current folder's name somewhere

# Editing
[x] allow for zooming in/out, reset (ctrl +/-/0)
[ ] when opening newly created notebook, write the title on top
[ ] list of existing tags when entering a new field
[ ] keep cursor position on reload
[x] Use a monospaced font
[ ] Use syntax highlighting (QSyntaxHighlighter), margins
[ ] The NewEntry form should not accept "ESC" as a cancel option if there is
    text in the TextEdit block.

# Preview
[x] allow for zooming in/out, reset (ctrl +/-/0)
[ ] better overall css style (bootstrap?)
[x] better css style for python (pygments)
[x] keep indentation for code
[ ] change the graphics of setFlat to match the disabled look, without the
    drawback of preventing scrolling.
[ ] have a "global" page, storing all notebooks, filter added with the
    notebooks' name as a tag


Future work
===========

[ ] colored icons and tags, with colors chosen by the user
[ ] support well multi-screen
[ ] use tox for automated testing

# Library
[ ] special graphic for shelves, maybe wood?
