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

class CFISDNews(NewsWebsite):

    def download_and_parse(self):

        text = requests.get(self.website).text

        tree = html.fromstring(text)

        for class_ in tree.find_class('index-item'):

            content = class_.getchildren()

            date = content[1].text_content().strip()
            # date = datetime.strptime(date, '%b. %d, %Y')

            title_elem = content[0].getchildren()[0]
            text = title_elem.text_content().strip()
            link = self.website + title_elem.attrib['href'][1:]

            add_news(self.school, 'CFISD Media', date, text, link, '', NewsType.TEXT)

class MustangMessenger(NewsWebsite):

    def download_and_parse(self):

        org_urls = {
            'Mustang News': ['/news/', '/news/page/2/'],
            'Mustang Sports': ['/sports/', '/sports/page/2/'],
            'Mustang Arts': ['/arts-and-entertainment/', '/arts-and-entertainment/page/2/'],
            'Mustang Students': ['/student-life/', '/student-life/page/2/'],
            'Mustang Editorial': ['/category/editorial-2/', '/editorial-2/page/2/']
        }

        self.run(org_urls)

    def run(self, org_urls):

        for org, urls in org_urls.items():

            for url in urls:

                text = requests.get(self.website + "category" + url).text

                tree = html.fromstring(text)

                for class_ in tree.find_class('sno-animate categorypreviewbox'):

                    try:
                        picture = class_.find_class('previewstaffpic')[0].attrib['src']
                    except (IndexError, KeyError):
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

class TheBridge(MustangMessenger):

    def download_and_parse(self):

        org_urls = {
            'Bridgeland News': ['/news/', '/news/page/2/'],
            'Bridgeland Opinion': ['/opinion/', '/opinion/page/2/'],
            'Bridgeland Sports': ['/sports/', '/sports/page/2/'],
            'Bridgeland Features': ['/features/', '/features/page/2/'],
            'Bridgeland Entertainment': ['/entertainment/', '/entertainment/page/2/']
        }

        self.run(org_urls)

class WingSpan(MustangMessenger):

    def download_and_parse(self):

        org_urls = {
            'Falls News': ['/news/', '/news/page/2/'],
            'Falls Opinion': ['/opinion/', '/opinion/page/2/'],
            'Falls Students': ['/student-life/', '/student-life/page/2/'],
            'Falls Entertainment': ['/entertainment/', '/entertainment/page/2/'],
            'Falls Faculty': ['/faculty/', '/faculty/page/2/']
        }

        self.run(org_urls)

class LakeView(MustangMessenger):

    def download_and_parse(self):

        org_urls = {
            'Lakes News': ['/news/', '/news/page/2/'],
            'Lakes Entertainment': ['/entertainment/', '/entertainment/page/2/'],
        }

        self.run(org_urls)

class Rampage(MustangMessenger):

    def download_and_parse(self):

        org_urls = {
            'Ram News': ['/news/', '/news/page/2/'],
            'Ram Opinion': ['/opinion/', '/opinion/page/2/'],
            'Ram Entertainment': ['/entertainment/', '/entertainment/page/2/'],
        }

        self.run(org_urls)

class Peregrine(MustangMessenger):

    def download_and_parse(self):

        org_urls = {
            'JV News': ['/news/', '/news/page/2/'],
            'JV Sports': ['/sports/', '/sports/page/2/'],
            'JV Students': ['/student-life/', '/student-life/page/2/'],
            'JV Opinion': ['/opinion/', '/opinion/page/2/'],
            'JV A&E': ['/ae/', '/ae/page/2/']
        }

        self.run(org_urls)

class Howler(MustangMessenger):

    def download_and_parse(self):

        org_urls = {
            'Langham News': ['/news/', '/news/page/2/'],
            'Langham Sports': ['/sports/', '/sports/page/2/'],
            'Langham Opinion': ['/opinion/', '/opinion/page/2/'],
            'Langham A&E': ['/ae/', '/ae/page/2/'],
            'Langham Students': ['/showcase/', '/showcase/page/2/']
        }

        self.run(org_urls)

student_news = {
    'bridgeland': TheBridge('bridgeland', 'http://bhsthebridge.com/'),
    'cypresscreek': 'https://www.cchspress.com/', # fix
    'cypressfalls': WingSpan('cypressfalls', 'https://www.cfwingspan.com/'),
    'cypresslakes': LakeView('cypresslakes', 'http://thelakeview.co/'),
    'cypresswoods': 'https://www.thecrimsonconnection.com/', #fix
    'cypressranch': MustangMessenger('cypressranch', 'https://cyranchnews.com/'),
    'cypressridge': Rampage('cypressridge', 'https://crhsrampage.com/'),
    'jerseyvillage': Peregrine('jerseyvillage', 'https://jvhsperegrine.com/'),
    'langhamcreek': Howler('langhamcreek', 'https://lchowler.net/'),
    'cfisd': CFISDNews('cfisd', 'https://www.cfisd.net/en/news-media/district/')
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
