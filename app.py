from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from main import get_wiki_text, StringFile
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
