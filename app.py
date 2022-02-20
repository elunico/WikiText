from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from main import get_wiki_text, StringFile
import os

app = Flask(__name__, static_url_path='/static')


@app.route('/')
def index():
    with open('templates/index.html') as f:
        return f.read()


@app.route('/api/extract')
def extract():
    url = request.args.get('url')
    isMarkdown = request.args.get('format') == 'markdown'
    if not url:
        return jsonify({'error': 'No url provided'})
    else:
        f = StringFile('')
        get_wiki_text(url, isMarkdown, f)
        return f.string


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=os.getenv("PORT"))
