from datetime import datetime
import json
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from cfisdapi import app

def fb_encode(val):
    return val.replace('/', '%2F').replace('.', '%2E').replace('_', '%5F')

def fb_decode(val):
    return val.replace('%2F', '/').replace('%2E', '.').replace('%5F', '_')

cred_json = json.loads(os.environ.get('FIREBASE_CRED', '{}'))
creds = credentials.Certificate(cred_json)
firebase_admin.initialize_app(creds)

db = firestore.client()
db_news = db.collection(u'news')
db_users = db.collection(u'users')

def set_grade(user, subject, name, grade, gradetype):
    """Sets a users grade in the db"""
    try:
        db_users.document(user).collection(u'grades').document(fb_encode(name)).set({
            u'name': name,
            u'subject': subject,
            u'grade': grade,
            u'gradetype': gradetype,
            u'lastupdated': datetime.now()
        })
    except Exception as e:
        print(e)

def add_user(user, demo):
    try:
        db_users.document(user).collection(u'profile').document(u'userdata').set({
            u'name': demo['name'],
            u'school': demo['school'],
            u'language': demo['language'],
            u'gender': demo['gender'],
            u'gradelevel': demo['gradelevel'],
            u'lastupdated': datetime.now()
        })
    except Exception as e:
        print(e)

def add_rank(user, transcript):
    """Adds a users class rank to db"""
    try:
        db_users.document(user).collection(u'transcript').document(u'gpa').set({
            u'gpa': transcript['gpa']['value'],
            u'rank': transcript['gpa']['rank'],
            u'classsize': transcript['gpa']['class_size'],
            u'lastupdated': datetime.now()
        })
    except Exception as e:
        print(e)

def add_news(school, organization, eventdate, text, link, picture, type_):
    """Adds new article to db"""
    try:
        db_news.document(fb_encode(school)).collection(u'articles').document(fb_encode(text)).set({
            u'school': school,
            u'text': text,
            u'organization': organization,
            u'link': link,
            u'picture': picture,
            u'articletype': type_,
            u'date': eventdate,
            u'lastupdated': datetime.now()
        })
    except Exception as e:
        print(e)

def get_news(school):
    """Gets all news from db"""
    try:
        all_news = db_news.document(fb_encode(school)).collection(u'articles').get()

        for article in all_news:
            yield article.to_dict()
    except Exception as e:
        print(e)
        return []
