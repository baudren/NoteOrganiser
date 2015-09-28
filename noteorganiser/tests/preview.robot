*** Settings ***
Resource        resource.robot


*** Test Cases ***
Filter a tag
    Open Note Organiser
    Open example notebook
    Filter for qml tag
    Only qml posts should show up
    [Teardown] remove qml tag

Browse tags from all notebooks
    Only tags from example notebook should be present
    Browse all tags
    More tags should be there
    [Teardown] reduce tags to current notebook

Color a tag
    TODO
    
Favorite a tag
    TODO
