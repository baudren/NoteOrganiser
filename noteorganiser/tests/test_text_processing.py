import os
from ..text_processing import extract_title_and_posts_from_text
from ..text_processing import from_notes_to_markdown
from .custom_fixtures import parent


def test_full_file(parent):
    source = os.path.join(parent.info.root, parent.info.notebooks[-1])
    text = open(source).readlines()
    title, posts = extract_title_and_posts_from_text(text)
    # Check that the title is correct
    assert title == 'Pyside'

    # Check that there is the right amount of posts
    assert len(posts) == 2

    # check that the whole file is well interpreted
    markdown, cleaned_tags = from_notes_to_markdown(source, [])
    assert len(cleaned_tags) == 6

    # check the reduction of tags
    #markdown, cleaned_tags = from_notes_to_markdown(source, [cleaned_tags[0]])


#def check_tag_sorting():
    #pass
