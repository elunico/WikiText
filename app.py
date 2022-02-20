from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import urllib.parse
from main import get_wiki_text, StringFile
import os

app = Flask(__name__, static_url_path='/static')


@app.route('/')
def index():
    with open('templates/index.html') as f:
        return f.read()


@app.route('/api/extract')
def extract():
    url = urllib.parse.unquote(request.args.get('url'))
    print(url)

    urlObject = urllib.parse.urlparse(url)
    if not urlObject.netloc.endswith('wikipedia.org'):
        return 'Error: Invalid URL. We only support wikipedia.org websites right now.', 400
    isMarkdown = request.args.get('format') == 'markdown'
    if not url:
        return 'Error: No url provided', 400
    else:
        f = StringFile('')
        try:
            get_wiki_text(url, isMarkdown, f)
        except:
            raise
            return 'Error: Failed to get extract wiki text from {}'.format(url), 500
        return f.string


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=os.getenv("PORT"))
