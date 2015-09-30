*** Settings ***
Resource        resource.robot


*** Test Cases ***
Create a new folder
    Open Note Organiser
    Create a new folder toto
    toto Folder should appear

Move notebooks to folders
    Drag and drop notebook example to folder toto
    Notebook example should be in folder toto
    Drag and drop notebook example to root
    [Teardown] Remove folder toto

Merge notebooks
    Drag and drop notebook example on notebook other
    Choose a new title
    Confirm merging
    Merged notebook should have all tags from both notebooks

Extract tag
    Open example notebook
    Separate qml tag into a new notebook named qml
    Notebook qml should exist

Export notebook to html
    Open example notebook
    Export notebook example to html

Export tags to html
    Browse all tags
    Select tags qml pyside
    Export selected tags to html
