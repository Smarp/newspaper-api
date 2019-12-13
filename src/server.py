#!/usr/bin/env python

from flask import Flask, request
from newspaper import Article, fulltext, Config, build
import os, json, re, html2text
from html.parser import HTMLParser

app = Flask(__name__)
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

linkedinUrl = 'https://www.linkedin.com/'

@app.route('/', methods = ['GET'])
@app.route('/topimage',methods = ['GET'])
def api_top_image():
    url = request.args.get('url')

    is_linkedin_url = url.startswith(linkedinUrl)
    if is_linkedin_url:
        config = Config()
        config.MAX_TITLE = 1000
        article = get_article(url, config)
        article = replace_title_text_from_title_url(article)
    else:
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


@app.route('/fulltext', methods=['POST'])
def text():
    html = request.get_data(as_text=True)
    text_result = call_simpler_html2text(html)
    return json.dumps({
        "text": text_result,
    }), 200, {'Content-Type': 'application/json'}


def call_simpler_html2text(html):
    extractor = configure_extractor()
    text_result = extractor.handle(html)
    return cleanup_extra_symbols(text_result)


def cleanup_extra_symbols(text_result):
    text_result = text_result.replace("#", "")
    text_result = text_result.replace("~~", "")
    text_result = re.sub(' +', ' ', text_result)
    text_result = re.sub('\n ', '\n', text_result).strip()
    text_result = re.sub('\n+', '\n', text_result).strip()
    return text_result


def configure_extractor():
    html_text = html2text.HTML2Text()
    html_text.ignore_links = True
    html_text.ignore_images = True
    html_text.ignore_emphasis = True
    html_text.hide_strikethrough = True
    html_text.abbr_title = True
    html_text.strong_mark = ""
    html_text.ul_item_mark = ""
    html_text.emphasis_mark = ""
    html_text.unicode_snob = True
    html_text.ignore_tables = True
    return html_text


def get_article(url, config = Config()):
    pdf_defaults = {"application/pdf": "%PDF-",
                    "application/x-pdf": "%PDF-",
                    "application/x-bzpdf": "%PDF-",
                    "application/x-gzpdf": "%PDF-"}
    article = Article(url, request_timeout=20, ignored_content_types_defaults=pdf_defaults, config=config)
    article.download()
    # uncomment this if 200 is desired in case of bad url
    # article.set_html(article.html if article.html else '<html></html>')
    article.parse()
    if article.text == "":
        paper = build(url, memoize_articles=False, fetch_images=False)
        article.text = paper.description
    return article


def html_to_text(html):
    try:
        return fulltext(html)
    except Exception:
        return ""


def replace_title_text_from_title_url(article):
    # try to fetch url linkedin post
    urls = find_urls(article.title)
    if len(urls)> 0:
        article_from_url = get_article(urls[0])
        article.title = article_from_url.title
        article.text = article_from_url.text
    else:
        # try to fetch url from HTML <title>
        parser = HtmlTagParser()
        parser.feed(article.html)
        if parser.tag_content['title'] != "":
            urls = find_urls(parser.tag_content['title'])
            if len(urls)> 0:
                article_from_url = get_article(urls[0])
                article.title = article_from_url.title
                article.text = article_from_url.text
    return article


class HtmlTagParser(HTMLParser):
    current_tag = ''
    tag_content = {}

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag

    def handle_endtag(self, tag):
        self.current_tag = ''

    def handle_data(self, data):
        self.tag_content[self.current_tag]=data


def find_urls(string):
    return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)

if __name__ == '__main__':
    port = os.getenv('NEWSPAPER_PORT', '38765')
    app.run(port=int(port), host='0.0.0.0')
