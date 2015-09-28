*** Settings ***
Resource        resource.robot


*** Test Cases ***
Create a notebook
    Open Note Organiser
    Create a notebook named titi
    The notebook titi should be present
    [Teardown] remove notebook titi

Create a folder
    Set option show hidden folders to False
    Create a folder named toto
    The folder toto should be absent
    Set option show hidden folders to True
    The folder toto should be present

Navigate a folder
    Navigate to the toto folder
    Folder should be empty
    Navigate one folder up
    [Teardown] remove folder toto
