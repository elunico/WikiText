from inspect import ismemberdescriptor
from bs4 import BeautifulSoup as bs
import requests
import sys
import argparse
import re


def parse_args():
    parser = argparse.ArgumentParser(description='Get plain text from a wikipedia article.')
    parser.add_argument('-u', '--url', help='The url of the website to parse.', required=True)
    parser.add_argument('-o', '--output', help='The output file to write the links to. Omit to write to stdout.', default='-')
    parser.add_argument('-m', '--markdown', help='Output in markdown format.', action='store_true')
    args = parser.parse_args()
    return args


class StringFile:
    def __init__(self, string):
        self.string = string

    def write(self, string):
        self.string += string

    def writelines(self, lines):
        self.write('\n'.join(lines))

    def close(self):
        pass


def get_wiki_text(url, isMarkdown, f):
    r = requests.get(url)
    soup = bs(r.text, 'html.parser')
    content = soup.find('div', {'id': 'mw-content-text'})
    try:
        for element in content.descendants:
            if element.name == 'p':
                if element.text.strip():
                    text = re.sub(r'\[\d+\]', '', element.text)
                    text = re.sub(r'\[\[(.*?)\]\]', r'\1', text)
                    f.write(text.strip())
                    f.write('\n\n')
            elif element.name is not None and element.name.startswith('h') and element.text.strip():
                if isMarkdown:
                    header = '#' * int(element.name[1])
                    f.write(header)
                    f.write(' ')
                f.write(element.text.strip())
                f.write('\n\n')
    except IOError:
        print('Failed to write to output file.')
        return False
    else:
        return True
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
