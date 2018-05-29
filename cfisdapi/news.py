from flask import request
from flask import jsonify
from lxml import html
import requests
import time
import re

from cfisdapi import app
from cfisdapi.database import get_news, add_news

class NewsType:
    """News Enum"""
    BASIC = 0
    ARTICLE = 1
    TEXT = 2

class NewsWebsite(object):

    def __init__(self, school, website):
        self.school = school
        self.website = website
        self.last_updated = 0

    def download_and_parse(self):
        pass

    def needs_update(self):
        return time.time() - self.last_updated > 86400

class MustangMessenger(NewsWebsite):

    def download_and_parse(self):

        org_urls = {
            'Mustang News': ['/news/', '/news/page/2/'],
            'Mustang Sports': ['/sports/', '/sports/page/2/'],
            'Mustang Arts': ['/arts-and-entertainment/', '/arts-and-entertainment/page/2/'],
            'Mustang Students': ['/student-life/', '/student-life/page/2/'],
            'Mustang Editorial': ['/category/editorial-2/', '/editorial-2/page/2/']
        }

        for org, urls in org_urls.items():

            for url in urls:

                text = requests.get(self.website + "category" + url).text

                tree = html.fromstring(text)

                for class_ in tree.find_class('sno-animate categorypreviewbox'):

                    try:
                        picture = class_.find_class('previewstaffpic')[0].attrib['src']
                    except IndexError:
                        continue

                    try:
                        text = class_.find_class('previewstaffpic')[0].attrib['alt'].encode("utf8")
                        text = text.decode("utf-8")
                    except IndexError:
                        continue

                    eventdate = class_.find_class('time-wrapper')[0].text_content().strip()
                    link = class_.xpath('a')[0].attrib['href']

                    add_news(self.school, org, eventdate, text, link, picture, NewsType.ARTICLE)

        self.last_updated = time.time()

student_news = {
    'bridgeland': 'http://bhsthebridge.com/', # TODO this will break
    'cypresscreek': 'https://www.cchspress.com/',
    'cypressfalls': 'https://www.cfwingspan.com/',
    'cypresslakes': 'http://thelakeview.co/',
    'cypresswoods': 'https://www.thecrimsonconnection.com/',
    'cypressranch': MustangMessenger('cypressranch', 'https://cyranchnews.com/'),
    'cypressridge': 'https://crhsrampage.com/',
    'jerseyvillage': 'https://jvhsperegrine.com/',
    'langhamcreek': 'https://lchowler.net/',
    'cfisd': '...'
}

@app.route("/api/news/<school>/all")
def get_all_news_list(school=""):
    """
    Get the news

    Returns
    -------
    str (json)
        All news articles associated with the given organization
    """

    if school == 'cyranch': # Tweak for CyRanch app
        school = 'cypressranch'

    if school in student_news:
        news_website = student_news[school]
    else:
        news_website = student_news['cfisd'] # Use general news
        school = 'cfisd'

    if news_website.needs_update():
        news_website.download_and_parse()

    news = {'news': {'all': []}}
    for article in get_news(school):
        news['news']['all'].append({
                                    'date': article[3].strftime("%B %d, %Y"),
                                    'image': article[6],
                                    'organization': article[2],
                                    'text': article[4],
                                    'link': article[5],
                                    'type': article[7]
                                   })
    return jsonify(news)
