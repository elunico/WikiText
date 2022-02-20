from inspect import ismemberdescriptor
from typing import List, Optional, Protocol, TextIO, Union

from bs4 import BeautifulSoup as bs, NavigableString, Tag
import requests
import sys
import argparse
import re


def parse_args():
    parser = argparse.ArgumentParser(description='Get plain text from a wikipedia article.')
    parser.add_argument('-u', '--url', help='The url of the website to parse.', required=True)
    parser.add_argument('-o', '--output', help='The output file to write the links to. Omit to write to stdout.',
                        default='-')
    parser.add_argument('-m', '--markdown', help='Output in markdown format.', action='store_true')
    args = parser.parse_args()
    return args


class Writeable(Protocol):
    def __init__(self, string: str):
        pass

    def write(self, string: str) -> None:
        pass

    def writelines(self, lines: List[str]) -> None:
        pass

    def close(self) -> None:
        pass


class StringFile:
    def __init__(self, string):
        self.string = string

    def write(self, string):
        self.string += string

    def writelines(self, lines):
        self.write('\n'.join(lines))

    def close(self):
        pass


def get_wiki_text(url: str, is_markdown: bool, f: Union[Writeable, TextIO]) -> bool:
    r = requests.get(url)
    soup = bs(r.text, 'html.parser')
    content = soup.find('div', {'id': 'mw-content-text'})
    try:
        for element in content.descendants:
            if element.name == 'p':
                iterator = element.descendants
                child_set = False
                child: Optional[Union[NavigableString, Tag]] = None
                while True:
                    try:
                        # on most loop iterations we need the next child
                        # if the while child in rest finds the next child and sets the flag
                        # we do not want to discard that child, but next turn we will unless it sets again
                        # please python add an unshift method to the iterators
                        if not child_set:
                            child = next(iterator)
                        else:
                            child_set = False
                        if (child is not None and
                                child.name == 'span' and
                                child.get('class', [None])[0] == 'mwe-math-element'):
                            if is_markdown:
                                # add the image links for formulae
                                image_src = child.find('img').get('src')
                                f.write(' ![]({}) '.format(image_src))
                            else:
                                # write the text formula but clean it up a little
                                f.write(child.text.replace('\n', ''))

                            # remove the rest of the descendants to prevent repeated formulas
                            rest = list(child.descendants)
                            oldChild = child
                            child = next(iterator)
                            while child in rest:
                                child = next(iterator)
                            child_set = True
                            # this loop finds the first child not in the span
                            # but the top of the loop discards it so we must set a flag here to indicate
                            # we have already found the next child so that it will not be discarded
                            # then we can remove the original span and all its children
                            oldChild.extract()

                        elif isinstance(child, str):
                            # going through descendants extracts all tags and all text subsequent to the tags
                            # so if we get some text that is not a formula just write it out to the file
                            if child:
                                text = re.sub(r'\[\d+]', '', child)
                                text = re.sub(r'\[\[(.*?)]]', r'\1', text)
                                f.write(text)
                    except StopIteration:
                        break
                f.write('\n\n')
            elif element.name is not None and element.name.startswith('h') and element.text.strip():
                if is_markdown:
                    header = '#' * int(element.name[1])
                    f.write(header)
                    f.write(' ')
                f.write(element.text.strip())
                f.write('\n\n')
        return True
    except IOError:
        print('Failed to write to output file.')
        return False

    finally:
        f.close()


def main():
    args = parse_args()
    url = args.url
    output = args.output

    f = open(output, 'w') if output != '-' else sys.stdout  # open output file or stdout
    get_wiki_text(url, args.markdown, f)


if __name__ == '__main__':
    main()
