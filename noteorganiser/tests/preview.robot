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
    Pick color red for tag qml
    Reopen Note Organiser
    Tag qml should be of color red
    [Teardown] pick color default for tag qml
    
Favorite a tag
    Ensure no tags are favorite
    Favorite tag qml 
    Reopen Note Organiser
    Tag qml should be the first tag
    [Teardown] unfavorite tag qml

Filter by relative date
    Create a random new post
    Filter posts no older than one day
    Random new post should be there

Filter by absolute date
    Open notebook example
    Preview date selection
    Adjust year range from 2013 to 2014
    4 posts should be present
