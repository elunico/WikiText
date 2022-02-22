import os
import re
import sys
import tempfile
import urllib.parse
import md2pdf

from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from stringfile import StringFile
from main import get_wiki_text

app = Flask(__name__, static_url_path='/static')
limiter = Limiter(app, key_func=get_remote_address)


def md2pdf_bytes(markdown_text, css_filename='default.css'):
    with tempfile.TemporaryDirectory() as d:
        md2pdf.md2pdf(os.path.join(d, 'temp.pdf'), markdown_text, css_file_path=os.path.join('resources', css_filename))
        with open(os.path.join(d, 'temp.pdf'), 'rb') as pdf:
            return pdf.read()


@app.route('/')
def index():
    with open('templates/index.html') as f:
        return f.read()


@app.route('/api/extract')
@limiter.limit("5/minute")
def extract():
    url = urllib.parse.unquote(request.args.get('url'))
    url_object = urllib.parse.urlparse(url)
    is_pdf = request.args.get('format') == 'pdf'
    is_markdown = request.args.get('format') == 'markdown' or is_pdf

    if not url:
        return 'Error: No url provided', 400
    if not url_object.netloc.endswith('wikipedia.org'):
        return 'Error: Invalid URL. We only support wikipedia.org websites right now.', 400

    f = StringFile('')
    try:
        get_wiki_text(url, is_markdown, f)
        text = f.string
        text = re.sub(r'\[\d+]', '', text)
        text = re.sub(r'\[([^\[\]]+?)]', r'', text)
        if is_pdf:
            return md2pdf_bytes(text)
        else:
            return text

    except (AttributeError, ValueError, TypeError, OSError) as e:
        print("Error on url='{}': {}".format(url, repr(e)), file=sys.stderr)
        return 'Error: Failed to get extract wiki text from {}'.format(url), 500


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=os.getenv("PORT"))
