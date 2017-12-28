from flask import request
from flask import jsonify
from lxml import html
import requests
import hashlib
import time
import re

from cfisdapi import app
from cfisdapi.database import get_news, add_news, get_news_orgs

class NewsType:
    """News Enum"""
    BASIC = 0
    ARTICLE = 1
    TEXT = 2

news_last_updated = 0 # Last time the news was updated
cyranch_pages = {'Mustang News': ['/news/', '/news/page/2/'],
                 'Mustang Sports': ['/sports/', '/sports/page/2/'],
                 'Mustang Arts': ['/arts-and-entertainment/', '/arts-and-entertainment/page/2/'],
                 'Mustang Students': ['/student-life/', '/student-life/page/2/'],
                 'Mustang Editorial': ['/category/editorial-2/', '/editorial-2/page/2/']}


def update_news(): # TODO Make this async
    """Updates the database with the lastest Cy-Ranch news articles."""
    for category in cyranch_pages.keys():

        print("Updating " + category)

        for url in cyranch_pages[category]:

            text = requests.get("http://cyranchnews.com/category" + url).text

            tree = html.fromstring(text)

            for class_ in tree.find_class('sno-animate categorypreviewbox'):

                picture = class_.find_class('previewstaffpic')[0].attrib['src']
                eventdate = class_.find_class('time-wrapper')[0].text_content().strip()
                text = class_.find_class('previewstaffpic')[0].attrib['alt'].encode("utf8")
                link = class_.xpath('a')[0].attrib['href']

                add_news(picture, category, eventdate, text, link, NewsType.ARTICLE, check=True)


@app.route("/api/news/cyranch/all")
def get_news():
    """
    Get the news

    Returns
    -------
    str (json)
        All news articles associated with the given organization
    """
    global news_last_updated
    if time.time() - news_last_updated > 86400: # 86400 = A Long enough time to update news
        news_last_updated = time.time()
        update_news()

    news = {'news': {'all': []}}
    for article in get_news():
        news['news']['all'].append({
                                    'date': article[4].strftime("%B %d, %Y"),
                                    'image': article[2],
                                    'organization': article[3],
                                    'text': article[5],
                                    'link': article[6],
                                    'type': article[7]
                                   })
    return jsonify(news)

# form_html = """
# <html>
# <head>
# </head>
# <body>
# <form action="/news/create" method="POST">
# <select name="organization">
# OPTIONS
# </select><br>
# Picture: <input type="text" name="pic"><br>
# Text: <input type="text" name="text"><br>
# Link: <input type="text" name="link"><br>
# Date: <input type="date" name="date"><br>
# Type (1=Article,2=Text): <input type="number" name="type"><br>
# Password: <input type="password" name="password"><br>
# <input type="submit" name="submit">
# </form>
# </body>
# </html>
# """

# @app.route("/news/create", methods=['GET', 'POST'])
# def create_org_news():
#     """
#     Creates a news item
#
#     This will add a new news article to the database. If the page is requested
#     from a GET a form will be displayed and if a POST is sent the form data will
#     be used to add the article to the database.
#     """
#     if request.method == 'POST':
#
#         pic = request.form['pic']
#         org = request.form['organization']
#         text = request.form['text']
#         link = request.form['link']
#         date = request.form['date']
#         password = request.form['password']
#
#         execute("select distinct icon from news where organization=%s", [org])
#         icon = fetchone()[0]
#
#         if hashlib.sha256(org + "!").hexdigest()[:8] == password:  # Still Not Secure
#
#             add_news(icon, pic, org, date, text, link, NewsType.ARTICLE)
#             return "Success"
#
#         return "Error"
#
#     else:
#
#         orgs = []
#
#         execute("select distinct organization from news")
#         for org in fetchall():
#             orgs.append(org[0])
#
#         return form_html.replace("OPTIONS","\n".join(map(lambda s: "<option value=\"{}\">{}</option>".format(s, s), orgs)))


@app.route("/api/news/cyranch/list")
def list_news():
    """
    Lists the news sources

    Returns
    -------
    str (json)
        A json with every news source and its respective icon location in the
        mobile app.
    """
    orgs = {'news': []}
    for org in get_news_orgs():
        orgs['news'].append(org)

    return jsonify(orgs)
