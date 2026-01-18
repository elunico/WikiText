import os
import sys
import uuid
import urllib.parse

from flask import Flask, make_response, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from parsing.main import extract_wiki_content
from util import after_render_hook, md2pdf_bytes

app = Flask(__name__, static_url_path='/static')
limiter = Limiter(get_remote_address, app=app)


@app.route('/')
def index():
    with open('templates/index.html') as f:
        return f.read()


@app.get('/robots.txt')
def robots():
    with open('../utilities/robots.txt') as f:
        r = make_response(f.read())
    r.headers['Content-Type'] = 'text/plain'
    return r


@app.route('/api/extract')
@limiter.limit("5/minute")
def extract():
    url = urllib.parse.unquote(request.args.get('url'))
    url_object = urllib.parse.urlparse(url)
    format = request.args.get('format')

    if not url:
        return 'Error: No url provided', 400
    if not url_object.netloc.endswith('wikipedia.org'):
        return 'Error: Invalid URL. We only support wikipedia.org websites right now.', 400

    try:
        article = extract_wiki_content(url)
        article.after_render_hook = after_render_hook

        if format == 'pdf':
            response = make_response(md2pdf_bytes(article.render_markdown()))
            response.headers['Content-Type'] = 'application/pdf'
            return response
        elif format == 'markdown':
            response = make_response(article.render_markdown())
            response.headers['Content-Type'] = 'text/markdown'
            response.headers['encoding'] = 'utf-8'
            return response
        else:
            response = make_response(article.render_text())
            response.headers['Content-Type'] = 'text/plain'
            response.headers['encoding'] = 'utf-8'
            return response

    except (AttributeError, ValueError, TypeError, OSError) as e:
        err_id = uuid.uuid4()
        print("[{}] Error on url='{}': {}".format(err_id, url, repr(e)))
        return '[{}] Error: Failed to get extract wiki text from {}'.format(err_id, url), 500
    except Exception as e:
        err_id = uuid.uuid4()
        print("[{}] Error on url='{}': {}".format(err_id, url, repr(e)))
        return '[{}] Error: The server encountered an unknown error {}'.format(err_id, url), 500


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=5000)
