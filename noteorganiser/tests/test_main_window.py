# Frame to test
from ..NoteOrganiser import NoteOrganiser

def test_initialisation(qtbot):
    # Specifying a different folder for storing everything (for testing
    # purposes)
    # Creating a NoteOrganiser and adding it to the bot
    note = NoteOrganiser()
    qtbot.addWidget(note)


