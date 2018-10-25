from urllib.parse import urlparse
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

create_rand_id = lambda: str(uuid.uuid4())

def set_grade(user, subject, name, grade, gradetype):
    """Sets a users grade in the db"""
    cur.execute("SELECT 1 FROM grades WHERE user_id=%s AND name=%s AND subject=%s;", [user, name, subject])
    if cur.fetchone() == None:
        cur.execute("INSERT INTO grades (user_id, name, subject, grade, gradetype) values (%s, %s, %s, %s, %s);",
                    [user, name, subject, grade, gradetype])
    else:
        cur.execute("UPDATE grades SET grade=%s, gradetype=%s WHERE user_id=%s AND name=%s AND subject=%s;",
                    [grade, gradetype, user, name, subject])
    conn.commit()

    return True

def is_user(user):
    """Checks if users exists in db"""
    cur.execute("SELECT 1 FROM demo WHERE user_id=%s;", [user])
    return cur.fetchone() != None

def add_user(user, demo):

    cur.execute("INSERT INTO demo (user_id, name, school, language, gender, gradelevel, updateddate) values (%s, %s, %s, %s, %s, %s, now());",
                [user, demo['name'], demo['school'], demo['language'], demo['gender'], demo['gradelevel']])
    conn.commit()

    return True

def add_rank(user, transcript):
    """Adds a users class rank to db"""
    cur.execute("SELECT 1 FROM rank WHERE user_id=%s;", [user])
    if cur.fetchone() == None:
        cur.execute("INSERT INTO rank (user_id, gpa, pos, classsize, updateddate) values (%s, %s, %s, %s, now());",
                    [user, transcript['gpa']['value'], transcript['gpa']['rank'], transcript['gpa']['class_size']])
    else:
        cur.execute("UPDATE rank SET pos=%s, classsize=%s, gpa=%s WHERE user_id=%s;",
                    [transcript['gpa']['rank'], transcript['gpa']['class_size'], transcript['gpa']['value'], user])
    conn.commit()

    return True

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
