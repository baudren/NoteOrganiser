"""custom utilities"""

from __future__ import unicode_literals
import re


def fuzzySearch(searchInput, baseString):
    """fuzzy comparison of the strings"""
    #normalize strings
    searchInput = re.sub(r'\s', r' ', searchInput.lower())
    baseString = re.sub(r'\s', r' ', baseString.lower())

    #normal substring comparison
    if searchInput in baseString:
        return True

    # split searchInput and check them separately
    if ' ' in searchInput:
        if not [subString for subString in searchInput.split(' ') if not
                fuzzySearch(subString, baseString)]:
            return True

    # no match found
    return False
