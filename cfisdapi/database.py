from urllib.parse import urlparse
from datetime import datetime
import json
import uuid
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from cfisdapi import app


cred_json = json.loads(os.environ.get('FIREBASE_CRED', '{}'))
creds = credentials.Certificate(cred_json)
firebase_admin.initialize_app(creds)

db = firestore.client()
db_news = db.collection(u'news')
db_users = db.collection(u'users')

create_rand_id = lambda: str(uuid.uuid4())

def set_grade(user, subject, name, grade, gradetype):
    """Sets a users grade in the db"""

    db_users.document(user).collection(u'grades').document(name).set({
        u'name': name,
        u'subject': subject,
        u'grade': grade,
        u'gradetype': gradetype
    })

def add_user(user, demo):

    db_users.document(user).collection(u'profile').document(u'userdata').set({
        u'name': demo['name'],
        u'school': demo['school'],
        u'language': demo['language'],
        u'gender': demo['gender'],
        u'gradelevel': demo['gradelevel'],
        u'lastupdated': datetime.now()
    })

def add_rank(user, transcript):
    """Adds a users class rank to db"""

    db_users.document(user).collection(u'transcript').document(u'gpa').set({
        u'gpa': transcript['gpa']['value'],
        u'rank': transcript['gpa']['rank'],
        u'classsize': transcript['gpa']['class_size'],
        u'lastupdated': datetime.now()
    })

def add_news(school, organization, eventdate, text, link, picture, type_):
    """Adds new article to db"""
    db_news.document(school).collection(u'articles').document(text).set({
        u'school': school,
        u'text': text,
        u'organization': organization,
        u'link': link,
        u'picture': picture,
        u'articletype': type_,
        u'date': eventdate
    })

def get_news(school):
    """Gets all news from db"""

    all_news = db_news.document(school).collection(u'articles').get()

    for article in all_news:
        yield article.to_dict()
