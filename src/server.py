#!/usr/bin/env python

import logging
from flask import Flask, request
from newspaper import Article, Config, build, extractors
import os
import json
import re
import html2text
from webpreview import web_preview
from urllib.parse import urlparse

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

linkedinUrl = 'https://www.linkedin.com/'
linkedinRedirectUrl = 'https://www.linkedin.com/redir/redirect'

CUSTOM_USER_AGENT = os.getenv('CUSTOM_USER_AGENT', Config().browser_user_agent)
CUSTOM_DOMAINS = set(os.getenv('CUSTOM_DOMAINS', '').split())

OG_TAG_METHOD = "ogtag"

from newspaper.cleaners import DocumentCleaner


# Patch document cleanup regex for custom element ids
def get_remove_nodes_regex(self):
    return self._remove_nodes_re


def set_remove_nodes_regex(self, value):
    if hasattr(self.config, 'cleanup_extra_ids'):
        extra_ids_re = "|".join(self.config.cleanup_extra_ids)
        self._remove_nodes_re = value + "|" + extra_ids_re
    else:
        self._remove_nodes_re = value


DocumentCleaner.remove_nodes_re = property(get_remove_nodes_regex, set_remove_nodes_regex)


@app.route('/health', methods=['GET'])
def health():
    return 'OK', 200


@app.route('/', methods=['GET'])
@app.route('/topimage', methods=['GET'])
def api_top_image():
    url = request.args.get('url')
    fetch_method = request.args.get('fetch_method')

    if fetch_method == OG_TAG_METHOD:
        return fetch_og_tags(url)

    return fetch_by_newspaper(url)


def is_linkedin_url(url):
    return url.startswith(linkedinUrl)


def is_linkedin_redirect_url(url):
    return url.startswith(linkedinRedirectUrl)


def fetch_by_newspaper(url):
    if is_linkedin_url(url):
        config = Config()
        # custom cleanup list for cookie banner
        config.cleanup_extra_ids = ["artdeco-global-alert-container", "artdeco-global-alerts-cls-offset"]
        config.MAX_TITLE = 1000
        article = get_article(url, config)
    else:
        article = get_article(url, config=get_config(url))
    return json.dumps({
        "authors": article.authors,
        "html": article.html,
        "images:": list(article.images),
        "movies": article.movies,
        "publish_date": article.publish_date.strftime("%s") if article.publish_date else None,
        "text": article.text,
        "title": article.title,
        "topimage": article.top_image}), 200, {'Content-Type': 'application/json'}


def fetch_og_tags_internal(url):
    return web_preview(url, timeout=20)


def fetch_og_tags(url):
    title, description, imageUrl = fetch_og_tags_internal(url)
    if imageUrl and not imageUrl.startswith("http") and not imageUrl.startswith("https"):
        urlParseResult = urlparse(url)
        imageUrl = urlParseResult.scheme + "://" + urlParseResult.netloc + imageUrl

    return json.dumps({
        "text": description,
        "title": title,
        "images:": list(imageUrl),
        "topimage": imageUrl
    }), 200, {'Content-Type': 'application/json'}


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


def get_article(url, config=Config()):
    pdf_defaults = {"application/pdf": "%PDF-",
                    "application/x-pdf": "%PDF-",
                    "application/x-bzpdf": "%PDF-",
                    "application/x-gzpdf": "%PDF-"}
    article = Article(url, request_timeout=20,
                      ignored_content_types_defaults=pdf_defaults, config=config)
    if is_linkedin_url(url):
        article.extractor = LinkedInContentExtractor(config=config)
    article.download()
    # uncomment this if 200 is desired in case of bad url
    # article.set_html(article.html if article.html else '<html></html>')
    article.parse()
    if article.text == "" and article.html != "%PDF-":
        article.text = get_text(article)
        if article.text == "":
            paper = build(url, memoize_articles=False, fetch_images=False)
            article.text = paper.description
    return article


def get_text(article):
    doc = article.clean_doc
    doc_description = article.extractor.get_meta_description(doc)
    nodes = doc.xpath('.//p[starts-with(text(),"' + doc_description[:10] + '")]')
    if not nodes:
        return doc_description
    children = nodes[0].getchildren()
    children_texts = list(map(lambda x: x.text + x.tail, children))
    article_text = (nodes[0].text + ''.join(children_texts)).replace(os.linesep, ' ').strip()
    return article_text if article_text else doc_description


class LinkedInContentExtractor(extractors.ContentExtractor):
    def __init__(self, config):
        extractors.ContentExtractor.__init__(self, config)

        # we store it here to pass to the is_boostable() function
        # otherwise we need to override the calculate_best_node() function that has too much logic
        # storing the doc here should not be a problem, since we create a new instance of extractor for every document
        self.doc = None

    def calculate_best_node(self, doc):
        self.doc = doc
        return extractors.ContentExtractor.calculate_best_node(self, doc)

    def is_boostable(self, node):
        doc_description = self.get_meta_description(self.doc)
        node_text = self.parser.getText(node)
        if doc_description and node_text and node_text.startswith(doc_description[:10]):
            return True
        return extractors.ContentExtractor.is_boostable(self, node)


def get_config(url):
    parseResult = urlparse(url)
    config = Config()
    if parseResult.hostname in CUSTOM_DOMAINS:
        config.browser_user_agent = CUSTOM_USER_AGENT

    return config


if __name__ == '__main__':
    port = os.getenv('NEWSPAPER_PORT', '38765')
    app.run(port=int(port), host='0.0.0.0')
