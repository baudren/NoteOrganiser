# A post is considered to be extracted from an existing file, and always
# consists in a title, followed by a line of '------------', followed
# immediatly by the tags with a leading #. It is a list of strings, where empty
# ones were removed.
# If it is a valid post, it has at minima 4 lines (title, line of -, tags,
# date)
# They should be extracted recursively, and fed to the different routines
# `_from_post`.
from datetime import date


def is_valid_post(post):
    """
    Check that it has all the required arguments

    >>> good = ["Toto", "-------", "# non-linear, pk", "*21/12/2012*"]
    >>> bad = ["Toto", "-------", "21/12/2012*"]
    >>> is_valid_post(good)
    True
    >>> is_valid_post(bad)
    False
    """
    is_valid = True
    if len(post) < 4:
        is_valid = False
    else:
        # Recover the index of the line of dashes, in case of long titles
        index = 0
        dashes = [e for e in post if e.find('----') != -1]
        try:
            index = post.index(dashes[0])
        except ValueError:
            is_valid = False
        if index:
            if not post[0]:
                is_valid = False
            if post[index+1] and post[index+1].find('#') == -1:
                is_valid = False
        # do a regexp for post[3]
    return is_valid


def extract_tags_from_post(post):
    """
    Recover the tags from an extracted post

    .. note::

        No tests are being done to ensure that the third line exists, as only
        valid posts, determined with :func:`is_valid_post` are sent to this
        routine.

    >>> post = ["Toto", "-------", " # non-linear, pk", "*21/12/2012*"]
    >>> extract_tags_from_post(post)
    ['non-linear', 'pk']
    """
    tag_line = post[2].strip()
    if tag_line and tag_line[0] == '#':
        tags = [elem.strip() for elem in tag_line[1:].split(',')]

    return tags


def extract_title_from_post(post):
    """
    Recover the title from an extracted post

    >>> post = ["Toto", "-------", "# non-linear, pk", "*21/12/2012*"]
    >>> extract_title_from_post(post)
    'Toto'
    >>> long = ["A very long", "title", "------", "# something"]
    >>> extract_title_from_post(long)
    'A very long title'
    """
    # If the title covers several line, it has to be fully recovered
    dashes = [e for e in post if e.find('----') != -1]
    dashline_index = post.index(dashes[0])

    title = ' '.join([post[index] for index in range(0, dashline_index)])

    return title


def extract_date_from_post(post):
    """
    Recover the date from an extracted post

    >>> post = ["Toto", "-------", "# non-linear, pk", "*21/12/2012*"]
    >>> extract_date_from_post(post)
    datetime.date(2012, 12, 21)
    """
    return date(2012, 12, 21)


def extract_corpus_from_post(post):
    """
    Recover the whole text

    >>> post = ["Toto", "-------", "# non-linear, pk", "*21/12/2012*",
    ...         "This morning I woke", "up and it was a nice weather"]
    >>> extract_corpus_from_post(post)
    ['This morning I woke', 'up and it was a nice weather']
    """
    return ["This morning I woke", "up and it was a nice weather"]


if __name__ == "__main__":
    import doctest
    doctest.testmod()
