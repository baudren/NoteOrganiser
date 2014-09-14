Roadmap for 0.2
===============

# General
[ ] Document more.
[ ] Improve keyboard shortcuts (ctrl instead of alt, etc).
[ ] Ensure proper resizing at all times.
[ ] Ensure proper key navigation at all times.
[x] Use py.test and qtbot module to test the individual functionalities.
    [x] replace calls to parent's methods by proper use of signal/slot
    [x] ensuring proper relative import for tests (for py27)
    [x] tests *actually* passing
    [ ] testing the right-click menu on buttons?

# Library
[ ] vector icons?
[ ] special graphic for shelves (wood?)
[ ] variable number of columns/line on the shelves
[ ] resizing should change the number of columns/lines for the shelves
[ ] Display all tags in this zone
[x] Create folder
[ ] Display the current folder's name somewhere

# Editing
[ ] allow for zooming
[ ] when opening newly created notebook, write the title on top
[ ] list of existing tags when entering a new field
[ ] keep cursor position on reload
[ ] Use a monospaced font
[ ] Use syntax highlighting (QSyntaxHighlighter), margins

# Preview
[ ] allow for zooming in (ctrl +)
[ ] better overall css style (bootstrap?)
[x] better css style for python (pygments)
[x] keep indentation for code
[ ] change the graphics of setFlat to match the disabled look, without the
    drawback of preventing scrolling.
[ ] have a "global" page, storing all notebooks, filter added with the
    notebooks' name as a tag


Future work
===========

[ ] colored icons, with colors chosen by the user
