*** Settings ***
Documentation       Assert the behaviour of the first time launch
...
...                 On the first opening, a choice has to be done to select
...                 a folder to store the notes.
Resource            resource.robot


*** Test Cases ***
First Time Visit
    Given I am a first time user
    When I launch the application
    And I am prompted with a choice of folder
    Then I can select a folder
    And the folder is remembered on quit
