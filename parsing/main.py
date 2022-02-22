import argparse
import re
import sys
from optparse import Option
from typing import Callable, List, Optional, TextIO, Union

import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from parsing.elements import Article, Header, MathElement, Paragraph, Text


def parse_args():
    parser = argparse.ArgumentParser(description='Get plain text from a wikipedia article.')
    parser.add_argument('-u', '--url', help='The url of the website to parse.', required=True)
    parser.add_argument('-o', '--output', help='The output file to write the links to. Omit to write to stdout.',
                        default='-')
    parser.add_argument('-m', '--markdown', help='Output in markdown format.', action='store_true')
    args = parser.parse_args()
    return args


def is_math_element(child):
    return (child.name == 'span' and
            child.get('class', [None])[0] == 'mwe-math-element')


def skip_all_descendants(child, iterator):
    rest = list(child.descendants)
    child = next(iterator)
    while child in rest:
        child = next(iterator)
    return child


def extract_wiki_content(url: str) -> Optional[Article]:
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    article = soup.find('div', {'id': 'mw-content-text'})
    content = []
    try:
        # all the content of a wikipedia article lives in mv-content-text
        # we will go through every descendant (recursively) of that div
        # to find all the content we care about so that it can be formatted correctly
        for element in article.descendants:
            # p elements contain the paragraphs of text content and math formulae images
            if element.name == 'p':
                paragraph = Paragraph()
                # we will go through all the children of the p to find math formulae separate from text
                iterator = element.descendants
                # needed for later, sometimes we do not want to advance the iterator
                child_set = False
                child: Optional[Union[NavigableString, Tag]] = None
                while True:
                    # iterate manually so we can skip children of math elements
                    try:
                        # a math element has its image src taken and all children removed from the tree so
                        # we only want to advance the iterator if the previous element did not do it for us
                        if not child_set:
                            child = next(iterator)
                        else:
                            child_set = False

                        if child is not None and is_math_element(child):
                            paragraph.append(MathElement(child.text.replace('\n', ''), child.find('img').get('src')))
                            # remove the rest of the descendants to prevent repeated formulas
                            # save a reference to the math span so it can be removed *AFTER* skipping descendants
                            # because otherwise beautiful soup will throw an error because it is not in the tree -.-
                            math_span = child
                            child = skip_all_descendants(child, iterator)
                            child_set = True
                            # this loop finds the first child not in the span
                            # but the top of the loop discards it so we must set a flag here to indicate
                            # we have already found the next child so that it will not be discarded
                            # then we can remove the original span and all its children
                            math_span.extract()
                        elif isinstance(child, str):
                            # going through descendants extracts all tags and all text subsequent to the tags
                            # so if we get some text that is not a formula just write it out to the file
                            if child:
                                text = re.sub(r'\[\d+]', '', child)
                                text = re.sub(r'\[([^\[\]]+?)]', r'', text)
                                paragraph.append(Text(text))
                    except StopIteration:
                        break
                # end each paragraph with a blank line
                content.append(paragraph)
            elif element.name is not None and element.name.startswith('h') and element.text.strip():
                content.append(Header(int(element.name[1]), element.text.strip()))
        return Article(content)
    except IOError:
        print('Failed to write to output file.')
        return None


def main():
    args = parse_args()
    url = args.url
    output = args.output

    f = open(output, 'w') if output != '-' else sys.stdout  # open output file or stdout
    extract_wiki_content(url, args.markdown, f)


if __name__ == '__main__':
    main()
