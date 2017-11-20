from flask import request
from flask import jsonify
from lxml import html
import requests
import hashlib
import time
import re

from cfisdapi import app
from cfisdapi.database import get_db_news, add_db_news, get_db_news_orgs

@app.route("/news/<org>")
def get_news_deprecated(org=""):

    news = []
    for article in get_db_news():
        if article[3] == org:
            news.append({
                        'date': article[4].strftime("%B %d, %Y"),
                        'image': article[2],
                        'organization': article[3],
                        'text': article[5],
                        'link': article[6],
                        'type': article[7],
                        'icon': ''
                        })
    return jsonify(news)

@app.route("/news/list")
def list_news_deprecated():
    """
    Lists the news sources

    Returns
    -------
    str (json)
        A json with every news source and its respective icon location in the
        mobile app.
    """
    orgs = {}
    for org in get_db_news_orgs():
        orgs[org] = ''

    return jsonify(orgs)
