import re
import ujson
import time
import requests
import hashlib
from flask import request

from cfisdapi import app
from cfisdapi.database import add_news, execute, fetchone, fetchall

class NewsType:
    BASIC = 0
    ARTICLE = 1
    TEXT = 2

re_get_cyranch_article = re.compile(
    r'<div class="sno-animate categorypreviewbox[\w\s]+"><a href="([\w\d:/.\-_]+)"><img src="([\w\d:/.\-_]+)" class="previewstaffpic" alt="[\w\s\S]+?" \/><\/a><h1 class="catprofile \w+"><a href="[\w\d:/.\-_]+" rel="bookmark">([\w\s\d&;#]+)<\/a><\/h1><p class="categorydate">(\w{3,10} \d{1,2}, \d{4})<\/p>')
cyranch_news_last = 0
cyranch_pages = {'Mustang News': ['/news/', '/news/page/2/'],
                 'Mustang Sports': ['/sports/', '/sports/page/2/'],
                 'Mustang Arts': ['/arts-and-entertainment/', '/arts-and-entertainment/page/2/'],
                 'Mustang Students': ['/student-life/', '/student-life/page/2/'],
                 'Mustang Opinion': ['/category/opinion-2/', '/opinion-2/page/2/']}


def update_cyranch_news():
    for category in cyranch_pages.keys():
        print "Updating " + category
        for url in cyranch_pages[category]:

            text = requests.get("http://cyranchnews.com/category" + url).text

            for a in re_get_cyranch_article.finditer(text):
                add_news("/icons/CyRanchMustangs.png",
                         a.group(2),
                         category,
                         a.group(4),
                         a.group(3).replace("&#8217;", "'").replace("&#8220;", "\"").replace("&#8221;", "\"").replace("&semi;", "").replace("&quot;", "'"),
                         a.group(1), NewsType.ARTICLE, check=True)


@app.route("/news/<org>")
def get_org_news(org=""):

    global cyranch_news_last
    if time.time() - cyranch_news_last > 86400:
        cyranch_news_last = time.time()
        update_cyranch_news()

    news = []
    if execute("select * from news where organization=%s", [org]):
        for n in fetchall():
            news.append({
                        'date': n[4].strftime("%B %d, %Y"),
                        'image': n[2],
                        'icon': n[1],
                        'organization': n[3],
                        'text': n[5],
                        'link': n[6],
                        'type': n[7]
                        })
    return ujson.dumps(news)

form_html = """
<html>
<head>
</head>
<body>
<form action="/news/create" method="POST">
<select name="organization">
OPTIONS
</select><br>
Picture: <input type="text" name="pic"><br>
Text: <input type="text" name="text"><br>
Link: <input type="text" name="link"><br>
Date: <input type="date" name="date"><br>
Type (1=Article,2=Text): <input type="number" name="type"><br>
Password: <input type="password" name="password"><br>
<input type="submit" name="submit">
</form>
</body>
</html>
"""


@app.route("/news/create", methods=['GET', 'POST'])
def create_org_news():
    if request.method == 'POST':
        pic = request.form['pic']
        org = request.form['organization']
        text = request.form['text']
        link = request.form['link']
        date = request.form['date']
        password = request.form['password']

        execute("select distinct icon from news where organization=%s", [org])
        icon = fetchone()[0]

        if hashlib.sha256(org + "!").hexdigest()[:8] == password:  # Still Not Secure
            add_news(icon, pic, org, date, text, link, NewsType.ARTICLE)
            return "Success"
        return "Error"
    else:
        orgs = []

        execute("select distinct organization from news")
        for org in fetchall():
            orgs.append(org[0])

        return form_html.replace("OPTIONS",
                                 "\n".join(map(lambda s: "<option value=\"{}\">{}</option>".format(s, s), orgs)))


@app.route("/news/list")
def list_news():
    orgs = {}
    execute("select distinct organization, icon from news")
    for org in fetchall():
        orgs.update({org[0]: org[1]})
    return ujson.dumps(orgs)
