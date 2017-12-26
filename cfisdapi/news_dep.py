"""
 _______                                                               __                      __
|       \                                                             |  \                    |  \
| $$$$$$$\  ______    ______    ______    ______    _______  ______  _| $$_     ______    ____| $$
| $$  | $$ /      \  /      \  /      \  /      \  /       \|      \|   $$ \   /      \  /      $$
| $$  | $$|  $$$$$$\|  $$$$$$\|  $$$$$$\|  $$$$$$\|  $$$$$$$ \$$$$$$\\$$$$$$  |  $$$$$$\|  $$$$$$$
| $$  | $$| $$    $$| $$  | $$| $$   \$$| $$    $$| $$      /      $$ | $$ __ | $$    $$| $$  | $$
| $$__/ $$| $$$$$$$$| $$__/ $$| $$      | $$$$$$$$| $$_____|  $$$$$$$ | $$|  \| $$$$$$$$| $$__| $$
| $$    $$ \$$     \| $$    $$| $$       \$$     \ \$$     \\$$    $$  \$$  $$ \$$     \ \$$    $$
 \$$$$$$$   \$$$$$$$| $$$$$$$  \$$        \$$$$$$$  \$$$$$$$ \$$$$$$$   \$$$$   \$$$$$$$  \$$$$$$$
                    | $$
                    | $$
                     \$$
"""
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
    news.append({
            'date': 'Jan 1, 2099',
            'image': 'https://cdn.pixabay.com/photo/2016/09/15/18/29/update-1672356_960_720.png',
            'organization': 'Mustang News',
            'text': 'Update Your App!!',
            'link': '#',
            'type': 1,
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
