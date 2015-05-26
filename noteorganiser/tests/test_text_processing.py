from __future__ import unicode_literals
import os
import pytest
from datetime import date
from ..text_processing import *
from .custom_fixtures import parent
from collections import OrderedDict as od

import six

def test_full_file(parent):
    # Full list of tags, to update
    tags = ['layout', 'widget', 'scroll', 'clear', 'button', 'disable']

    source = os.path.join(parent.info.root, parent.info.notebooks[-1])
    text = open(source).readlines()
    # Add an extra blanck line at the beginning of the text
    text = ["   \t   \n"] + text
    title, posts = extract_title_and_posts_from_text(text)
    # Check that the title is correct
    assert title == 'Pyside'

    # Check that there is the right amount of posts
    assert len(posts) == 2

    # check that the whole file is well interpreted with no tags in input
    markdown, extracted_tags = from_notes_to_markdown(source, [])
    assert len(extracted_tags) == 6
    keys = [e for e in extracted_tags.keys()]
    assert set(keys) == set(tags)

    # check the reduction of tags
    markdown, reduced_tags = from_notes_to_markdown(source, ['layout'])
    reduced_keys = [e for e in reduced_tags]
    assert len(reduced_tags) == 3
    assert set(reduced_keys) == set(['layout', 'widget', 'clear'])


def test_tag_sorting():
    source = ['toto', 'toto', 'toto', 'tata', 'titi', 'titi', 'titi', 'titi']
    ordered_keys = ['titi', 'toto', 'tata']
    output = sort_tags(source)
    # Check the output type
    assert isinstance(output, od)

    # Check the order
    assert [k for k in output.keys()] == ordered_keys


def test_extract_tags_from_post():
    # Check for a good post
    post = ['Toto', '-------', ' # non-linear, pk', '*21/12/2012*']
    tags, clean_post = extract_tags_from_post(post)
    assert len(tags) == 2
    assert tags == ['non-linear', 'pk']
    assert clean_post == ['Toto', '-------', '*21/12/2012*']

    # Check for empty tags
    empty_tag_post = ['Toto', '-------', '# ', '*21/12/2012*']
    with pytest.raises(ValueError):
        tags, clean_post = extract_tags_from_post(empty_tag_post)


def test_is_valid_post():

    good = ["Toto", "-------", "# non-linear, pk", "*21/12/2012*"]
    assert is_valid_post(good)

    with pytest.raises(ValueError):
        is_valid_post(["Toto", "-------", "*21/12/2012*"])

    with pytest.raises(ValueError):
        is_valid_post(["Toto", "-----", "# something", "12/12/042*"])

    with pytest.raises(ValueError):
        is_valid_post(['Toto', '=======', '# something', '*21/12/2012*'])

    with pytest.raises(ValueError):
        is_valid_post(['', '-------', '# non-linear, pk', '*21/12/2012*'])

    with pytest.raises(ValueError):
        is_valid_post(['Toto', '-------', '*21/12/2012*', 'something'])


def test_extract_corpus_from_post():
    post = ["Toto", "-------", "# non-linear, pk", "*21/12/2012*",
            "This morning I woke", "", "up and it was a nice weather"]
    answer = extract_corpus_from_post(post)
    assert answer == ['This morning I woke', '',
                      'up and it was a nice weather']


def test_extract_title_from_post():
    post = ["Toto", "-------", "# non-linear, pk", "*21/12/2012*"]
    answer = extract_title_from_post(post)
    assert answer == 'Toto'


def test_extract_date_from_post():
    post = ["Toto", "-------", "*21/12/2012*", "Something something"]
    post_date, clean_post = extract_date_from_post(post)
    assert post_date == date(2012, 12, 21)
    assert clean_post == ['Toto', '-------', 'Something something']
    with pytest.raises(ValueError):
        extract_date_from_post(["Toto", "---------", "meh"])


def test_normalize_post():
    post = ['Toto', 'has a long title', '-------', '# bla', '*08/11/2010*']
    answer = normalize_post(post)
    assert answer == ['Toto has a long title', '-------',
                      '# bla', '*08/11/2010*']
    assert is_valid_post(answer)
