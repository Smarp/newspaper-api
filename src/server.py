#!/usr/bin/env python

from flask import Flask, request
from newspaper import Article, fulltext, Config
import os, json, re

app = Flask(__name__)
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

linkedinPostUrl = 'https://www.linkedin.com/posts'

@app.route('/', methods = ['GET'])
@app.route('/topimage',methods = ['GET'])
def api_top_image():
    url = request.args.get('url')

    config = Config()
    if url.startswith(linkedinPostUrl):
        config.MAX_TITLE=1000

    article = get_article(url, config)

    if url.startswith(linkedinPostUrl):
        article = replace_title_text_from_title_url(article)

    return json.dumps({
            "authors": article.authors,
            "html": article.html,
            "images:": list(article.images),
            "movies": article.movies,
            "publish_date": article.publish_date.strftime("%s") if article.publish_date else None,
            "text": article.text,
            "title": article.title,
            "topimage": article.top_image}), 200, {'Content-Type': 'application/json'}


@app.route('/fulltext', methods=['POST'])
def text():
    html = request.get_data()
    return json.dumps({
        "text": html_to_text(html),
        }), 200, {'Content-Type': 'application/json'}


def get_article(url, config):
    pdf_defaults = {"application/pdf": "%PDF-",
                    "application/x-pdf": "%PDF-",
                    "application/x-bzpdf": "%PDF-",
                    "application/x-gzpdf": "%PDF-"}
    article = Article(url, request_timeout=20, ignored_content_types_defaults=pdf_defaults, config=config)
    article.download()
    # uncomment this if 200 is desired in case of bad url
    # article.set_html(article.html if article.html else '<html></html>')
    article.parse()
    return article


def html_to_text(html):
    try:
        return fulltext(html)
    except Exception:
        return ""

def replace_title_text_from_title_url(article):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', article.title)
    if len(urls)> 0:
        article_from_url = get_article(urls[0], Config())
        article.title = article_from_url.title
        article.text = article_from_url.text
    return article


if __name__ == '__main__':
    port = os.getenv('NEWSPAPER_PORT', '38765')
    app.run(port=int(port), host='0.0.0.0')
