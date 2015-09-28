*** Settings ***
Resource        resource.robot


*** Test Cases ***
Adding a post
    Open Note Organiser
    Create a random new post
    Verify the preview is updated
    Assert the new tags are there

Edit a post
    Right-click on last edited post
    Editor should be opened

Set an external editor
    Double click on last edited post
    User-defined editor should be opened


