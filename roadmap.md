Roadmap for 0.1
===============

# General
[x] create an Information class, holding all the necessary information, shared
    among every frame or widget.
[x] include an example notebook, for the syntax.
[x] add a link to the modified markdown syntax in the README.
[x] Include a setup.py script, with installation
[ ] Create the folder .noteorganiser, copy there pyside.md if not present.
[ ] Use Travis
[ ] Send the logger to a file

# Library
[x] remake icons
    [x] use own icons
    [x] write the names in the transparent zone
[x] allow for folders
[x] navigation options (back (i.e. up)), toolbar maybe?
[x] allow for removing notebook with right click
    [x] removing with right click
    [x] confirmation if non empty

# Editing
[x] allow for folders
[x] reload from disk externally modified files
[x] save modified files
[x] shortcut for previewing
[x] implement "new field"
    [x] form created
    [x] update the file

# Previewing
[x] script to convert modified md to md, then pandoc to html
[x] style-sheet support for web-browser
[x] list of existing tags, toggable buttons.
    [x] list appear
    [x] toggling buttons reduce the posts
    [x] full list of tags, with scrolling
    [x] fix the display (background color) (widgets not properly removed)
    [x] scrolling when a button is checked should work


Future work
===========

# General
[ ] Improve keyboard shortcuts (ctrl instead of alt, etc)
[ ] Ensure proper resizing at all times

# Library
[ ] vector icons?
[ ] special graphic for shelves (wood?)
[ ] variable number of columns/line on the shelves
[ ] resizing should change the number of columns/lines for the shelves

# Editing
[ ] when opening newly created notebook, write the title on top
[ ] list of existing tags when entering a new field
[ ] keep cursor position on reload
[ ] Use a monospaced font
[ ] Use syntax highlighting (QSyntaxHighlighter), margins

# Preview
[ ] allow for zooming in (ctrl +)
[ ] change the graphics of setFlat to match the disabled look, without the
    drawback of preventing scrolling.
[ ] have a "global" page, storing all notebooks, filter added with the
    notebooks' name as a tag
