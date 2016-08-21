#!/usr/bin/env python

from flask import Flask, url_for, request
from newspaper import Article
import os, json

app = Flask(__name__)

@app.route('/', methods = ['GET'])
@app.route('/topimage',methods = ['GET'])
def api_top_image():
    url = request.args.get('url')
    article = get_article(url)
    return json.dumps({
        "topimage": article.top_image,
        "text": article.text,
        "authors":article.authors,
        "movies": article.movies,
        "publish_date": article.publish_date,
        "html": article.html})

def get_article(url):
    article = Article(url, request_timeout=20)
    article.download()
    article.parse()
    return article

if __name__ == '__main__':
    port = os.getenv('NEWSPAPER_PORT', '38765')
    app.run(port=int(port), host='0.0.0.0')
