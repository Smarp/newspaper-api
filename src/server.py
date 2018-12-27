#!/usr/bin/env python

from flask import Flask, url_for, request
from newspaper import Article
import os, json
import requests

EMPTY_PDF_RESPONSE = json.dumps(
    {"authors": '',
     "html": '%PDF-',
     "images:": [],
     "movies": [],
     "publish_date": '',
     "text": '',
     "title": '',
     "topimage": ''}), 200, {'Content-Type': 'application/json'}

app = Flask(__name__)
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/', methods = ['GET'])
@app.route('/topimage',methods = ['GET'])
def api_top_image():
    url = request.args.get('url')
    if is_content_pdf(url):
        return EMPTY_PDF_RESPONSE
    article = get_article(url)
    return json.dumps({
        "authors": article.authors,
        "html": article.html,
        "images:": list(article.images),
        "movies": article.movies,
        "publish_date": article.publish_date.strftime("%s") if article.publish_date else None,
        "text": article.text,
        "title": article.title,
        "topimage": article.top_image}), 200, {'Content-Type': 'application/json'}


def is_content_pdf(url):
    response = requests.head(url)
    return response.headers['Content-Type'] == 'application/pdf'


def get_article(url):
    pdf_defaults = {"application/pdf": "%PDF-",
                    "application/x-pdf": "%PDF-",
                    "application/x-bzpdf": "%PDF-",
                    "application/x-gzpdf": "%PDF-"}
    article = Article(url, request_timeout=20, ignored_content_types_defaults=pdf_defaults)
    article.download()
    # uncomment this if 200 is desired in case of bad url
    # article.set_html(article.html if article.html else '<html></html>')
    article.parse()
    return article

if __name__ == '__main__':
    port = os.getenv('NEWSPAPER_PORT', '38765')
    app.run(port=int(port), host='0.0.0.0')
