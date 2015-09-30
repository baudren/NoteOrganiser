*** Settings ***
Resource        resource.robot


*** Test Cases ***
Adding a post
    Open Note Organiser
    Create a random new post
    Verify the preview is updated
    Assert the new tags are there

Preview the post while writing
    Create a post
    Type text and verify the mini-preview is updated
    [Teardown] Abort new post

Drag and drop images in post
    Create a post
    Drag and drop image from folder
    Link to image should be present in post
    Validate new post
    Image should be present in the html

Edit a post
    Ensure no external editor is defined
    Double click on an existing post
    Internal editor should be opened at the right place

Set an external editor
    Define an external editor
    Double click on an existing post
    User-defined editor should be opened at the right place


