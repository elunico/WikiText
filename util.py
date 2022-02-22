import md2pdf
import os
import re
import tempfile


def after_render_hook(text: str) -> str:
    text = re.sub(r'\[\d+]', '', text)
    text = re.sub(r'\[([^\[\]]+?)]', r'', text)
    return text


def md2pdf_bytes(markdown_text: str, css_filename: str = 'default.css') -> bytes:
    with tempfile.TemporaryDirectory() as d:
        md2pdf.md2pdf(os.path.join(d, 'temp.pdf'), markdown_text, css_file_path=os.path.join('resources', css_filename))
        with open(os.path.join(d, 'temp.pdf'), 'rb') as pdf:
            return pdf.read()
