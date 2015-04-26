# A post is considered to be extracted from an existing file, and always
# consists in a title, followed by a line of '------------', followed
# immediatly by the tags with a leading #. It is a list of strings, where empty
# ones were removed.
# If it is a valid post, it has at minima 4 lines (title, line of -, tags,
# date)
# They should be extracted recursively, and fed to the different routines
# `_from_post`.
# Note that all doctests are commented, and now executed in the py.test suite,
# for compatibility reasons between py2.7 and py3.3
from __future__ import unicode_literals
from datetime import date
from collections import Counter
from collections import OrderedDict as od
import re
import io


def is_valid_post(post):
    """
    Check that it has all the required arguments

    If the post is valid, the function returns True. Otherwise, an
    MarkdownSyntaxError is raised with a description of the problem.

    #>>> good = ["Toto", "-------", "# non-linear, pk", "*21/12/2012*"]
    #>>> is_valid_post(good)
    #True

    #>>> is_valid_post(["Toto", "-------", "*21/12/2012*"])
    #Traceback (most recent call last):
        #...
    #MarkdownSyntaxError: Post contains under four lines
    #>>> is_valid_post(["Toto", "-----", "# something", "12/12/042*"])
    #Traceback (most recent call last):
        #...
    #MarkdownSyntaxError: The date could not be read
    #>>> is_valid_post(['Toto', '=======', '# something', '*21/12/2012*'])
    #Traceback (most recent call last):
        #...
    #MarkdownSyntaxError: Post does not contain dashes
    #>>> is_valid_post(['', '-------', '# non-linear, pk', '*21/12/2012*'])
    #Traceback (most recent call last):
        #...
    #MarkdownSyntaxError: Post title is empty
    #>>> is_valid_post(['Toto', '-------', '*21/12/2012*', 'something'])
    #Traceback (most recent call last):
        #...
    #MarkdownSyntaxError: Tags were not found after the dashes
    """
    # remove all blank lines
    temp = [e for e in post if e]
    if len(temp) < 4:
        raise MarkdownSyntaxError("Post contains under four lines", post)
    else:
        # Recover the index of the line of dashes, in case of long titles
        index = 0
        dashes = [e for e in temp if re.match('^-{2,}$', e)]
        try:
            index = temp.index(dashes[0])
        except IndexError:
            raise MarkdownSyntaxError("Post does not contain dashes", post)
        if index:
            if not temp[0]:
                raise MarkdownSyntaxError("Post title is empty", post)
            if not re.match('^#.*$', temp[index+1]):
                raise MarkdownSyntaxError(
                    "Tags were not found after the dashes", post)
            match = re.match(
                r"^\*[0-9]{2}/[0-1][0-9]/[0-9]{4}\*$",
                temp[index+2])
            if not match:
                raise MarkdownSyntaxError(
                    "The date could not be read", temp)
    return True


def extract_tags_from_post(post):
    """
    Recover the tags from an extracted post

    .. note::

        No tests are being done to ensure that the third line exists, as only
        valid posts, determined with :func:`is_valid_post` are sent to this
        routine.

    #>>> post = ['Toto', '-------', ' # non-linear, pk', '*21/12/2012*']
    #>>> extract_tags_from_post(post)
    #(['non-linear', 'pk'], ['Toto', '-------', '*21/12/2012*'])
    """
    tag_line = post[2].strip()
    if tag_line and tag_line[0] == '#':
        tags = [elem.strip().lower() for elem in tag_line[1:].split(',')]

    return tags, post[:2]+post[3:]


def extract_title_from_post(post):
    """
    Recover the title from an extracted post

    #>>> post = ["Toto", "-------", "# non-linear, pk", "*21/12/2012*"]
    #>>> extract_title_from_post(post)
    #'Toto'
    """
    return post[0]


def extract_date_from_post(post):
    """
    Recover the date from an extracted post, and return the correct post

    #>>> post = ["Toto", "-------", "*21/12/2012*", "Something something"]
    #>>> extract_date_from_post(post)
    #(datetime.date(2012, 12, 21), ['Toto', '-------', 'Something something'])
    #>>> extract_date_from_post(["Toto", "---------", "meh"])
    #Traceback (most recent call last):
        #...
    #MarkdownSyntaxError: No date found in the post
    """
    for index, line in enumerate(post):
        match = re.match(
            r"\*([0-9]{2})/([0-1][0-9])/([0-9]{4})\*",
            line)
        if match:
            assert len(match.groups()) == 3
            day, month, year = match.groups()
            extracted_date = date(int(year), int(month), int(day))
            return extracted_date, post[:index]+post[index+1:]
    raise MarkdownSyntaxError("No date found in the post", post)


def normalize_post(post):
    """
    If a title has several lines, merge them

    #>>> post = ['Toto', 'has a long title', '-------', '# bla', '*08/11/2010*']
    #>>> normalize_post(post)
    #['Toto has a long title', '-------', '# bla', '*08/11/2010*']
    #>>> is_valid_post(_)
    #True
    """
    # Remove trailing \n
    post = [line.rstrip('\n') for line in post]

    # Recover the dashline (title of the post)
    dashes = [e for e in post if re.match('^-{2,}$', e)]
    dashline_index = post.index(dashes[0])

    title = ' '.join([post[index] for index in range(dashline_index)])
    normalized_post = [title]
    normalized_post.extend(post[dashline_index:])

    return normalized_post


def extract_corpus_from_post(post):
    """
    Recover the whole content of a post

    #>>> post = ["Toto", "-------", "# non-linear, pk", "*21/12/2012*",
    #...         "This morning I woke", "", "up and it was a nice weather"]
    #>>> extract_corpus_from_post(post)
    #['This morning I woke', '', 'up and it was a nice weather']
    """
    return post[4:]


def extract_title_and_posts_from_text(text):
    """
    From an entire text (array), recover each posts and the file's title

    """
    # Make a first pass to recover the title (first line that is underlined
    # with = signs) and the indices of the dash, that signals a new post.
    post_starting_indices = []
    has_title = False
    for index, line in enumerate(text):
        # Remove white lines at the beginning
        if not line.strip():
            continue
        if re.match('^={2,}$', line) and not has_title:
            title = ' '.join(text[:index]).strip()
            has_title = True
        if re.match('^-{2,}$', line) and line[0] == '-':
            # find the latest non empty line
            for backward_index in range(1, 10):
                if not text[index-backward_index].strip():
                    post_starting_indices.append(index-backward_index+1)
                    break

    if not has_title:
        raise MarkdownSyntaxError(
            "You should specify a title to your file"
            ", underlined with = signs", [])
    number_of_posts = len(post_starting_indices)

    # Create post_indices such that it stores all the post, so the starting and
    # ending index of each post
    post_indices = []
    for index, elem in enumerate(post_starting_indices):
        if index < number_of_posts - 1:
            post_indices.append([elem, post_starting_indices[index+1]])
        else:
            post_indices.append([elem, len(text)])

    posts = []
    for elem in post_indices:
        start, end = elem
        posts.append(text[start:end])

    # Normalize them all
    for index, post in enumerate(posts):
        posts[index] = normalize_post(post)
        assert is_valid_post(posts[index]) is True

    return title, posts


def from_notes_to_markdown(path, input_tags=None):
    """
    From a file, given tags, produce an output markdown file.

    This will then be interpreted with the pandoc library into html.

    ..note::

        so far the date is ignored.

    Returns
    -------
    markdown : list
        entire markdown text
    tags : list of tuples
        list of tags extracted from the text, with their importance
    """
    # Create the array to return
    text = io.open(path, 'r', encoding='utf-8', errors='replace').readlines()
    title, posts = extract_title_and_posts_from_text(text)
    markdown = ["# %s" % title, ""]
    extracted_tags = []
    for post in posts:
        name = extract_title_from_post(post)
        text = ["", "## %s" % name, ""]

        tags, post = extract_tags_from_post(post)
        if not all([tag in tags for tag in input_tags]):
            continue
        edit_date, post = extract_date_from_post(post)
        corpus = extract_corpus_from_post(post)
        text.extend(corpus)
        text.extend(["", ""])
        # Store the recovered tags
        extracted_tags.extend(tags)
        markdown.extend(text)

    cleaned_tags = sort_tags(extracted_tags)
    return markdown, cleaned_tags


def sort_tags(source):
    """
    return a sorted version of source, with the biggests tags first
    """
    output = od(sorted(Counter([e for e in source]).items(),
                key=lambda t: -t[1]))
    return output


def create_post_from_entry(title, tags, corpus):
    """
    Create a string containing the post given user's input

    """
    text = [title]
    text.append('\n%s\n' % ''.join(['-' for _ in range(len(title))]))
    text.append('# %s\n' % ', '.join(tags))
    text.append('\n*%s*\n\n' % date.today().strftime("%d/%m/%Y"))
    text.append(corpus+'\n')
    return ''.join(text)


class MarkdownSyntaxError(ValueError):

    def __init__(self, message, post):
        ValueError.__init__(self, message+':\n\n' +
                            '\n'.join(['    %s' % e for e in post]))
