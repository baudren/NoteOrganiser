import os
from ..text_processing import extract_title_and_posts_from_text
from ..text_processing import from_notes_to_markdown
from ..text_processing import sort_tags
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


def check_tag_sorting():
    source = {'toto': 3, 'tata': 1, 'titi': 10}
    ordered_keys = ['titi', 'toto', 'tata']
    output = sort_tags(source)
    # Check the output type
    assert isinstance(output, od)

    # Check the order
    assert [k for k in output.keys()] == ordered_keys
