"""tests for utilities"""

import os
import shutil
import datetime
from PySide import QtGui
from PySide import QtCore

#utils to test
from ..utils import fuzzySearch
from .custom_fixtures import parent


def test_fuzzySearch():
    ### these should return True

    #starts with the searchstring
    assert fuzzySearch('g', 'git got gut')
    #starts with the (longer) searchstring
    assert fuzzySearch('git', 'git got gut')
    #searchstring not at the start
    assert fuzzySearch('got', 'git got gut')
    #multiple substrings (separated by a space) found somewhere in the string
    assert fuzzySearch('gi go', 'git got gut')
    #empty string
    assert fuzzySearch('', 'git got gut')
    #strange whitespace
    assert fuzzySearch('gi   go', 'git  got gut')
    assert fuzzySearch('gi	go', 'git  got gut')

    ### these should return False

    #searchstring not found
    assert not fuzzySearch('bot', 'git got gut')
    #searchstring not found
    assert not fuzzySearch('gran', 'this is a great neat thing')
