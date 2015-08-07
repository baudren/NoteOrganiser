*** Keywords ***
I am a first time user
    Clean all stored settings

I launch the application
    Open Note Organiser

I am prompted with a choice of folder
    Folder Choice Should Be Present

I can select a folder
    ${folder} =             Pick a storage folder for the first time
    Set Test Variable       ${folder}

The folder is remembered on quit
    Close Note Organiser
    Open Note Organiser
    ${actual} =                 Get Storage Folder
    Should Be Equal As Strings  ${folder}   ${actual}
    
