import urlparse
import os

from cfisdapi import app

LOCAL = False # Running Locally = W/O Database

try:
    # If the VAR exists this probably is attach to a database
    url = urlparse.urlparse(os.environ["DATABASE_URL"])
    urlparse.uses_netloc.append("postgres")

    import psycopg2

    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    cur = conn.cursor()

except Exception as e:

    print("Running Locally b/c " + str(e))
    LOCAL = True

def db_wrapper(func):
    """Wrapper for database methods"""
    def wrapper(*args, **kwargs):
        if not LOCAL:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print('db error: ' + str(e) + ' @ ' + str(func))
                conn.rollback()
        return False
    return wrapper

@db_wrapper
def set_grade(user, subject, name, grade, gradetype):
    """Sets a users grade in the db"""
    cur.execute("SELECT 1 FROM grades WHERE user_id=%s AND name=%s AND subject=%s;", [user, name, subject])
    if cur.fetchone() == None:
        cur.execute("INSERT INTO grades (user_id, name, subject, grade, gradetype) values (%s,%s,%s,%s,%s);",
                    [user, name, subject, grade, gradetype])
    else:
        cur.execute("UPDATE grades SET grade=%s, gradetype=%s WHERE user_id=%s AND name=%s AND subject=%s;",
                    [grade, gradetype, user, name, subject])
    conn.commit()

    return True

@db_wrapper
def is_user(user):
    """Checks if users exists in db"""
    cur.execute("SELECT 1 FROM demo WHERE user_id=%s;", [user])
    return cur.fetchone() != None

@db_wrapper
def add_user(user, demo):

    cur.execute("INSERT INTO demo (user_id, name, school, language, gender, gradelevel) values (%s,%s,%s,%s,%s,%s);",
                [user, demo['name'], demo['school'], demo['language'], demo['gender'], demo['gradelevel']])
    conn.commit()

    return True

@db_wrapper
def add_rank(user, transcript):
    """Adds a users class rank to db"""
    cur.execute("SELECT 1 FROM rank WHERE user_id=%s;", [user])
    if cur.fetchone() == None:
        cur.execute("INSERT INTO rank (user_id, gpa, pos, classsize) values (%s,%s,%s,%s);",
                    [user, transcript['gpa']['value'], transcript['gpa']['rank'], transcript['gpa']['class_size']])
    else:
        cur.execute("UPDATE rank SET pos=%s, classsize=%s, gpa=%s WHERE user_id=%s;",
                    [transcript['gpa']['rank'], transcript['gpa']['class_size'], transcript['gpa']['value'], user])
    conn.commit()

    return True

@db_wrapper
def add_news(picture, organization, eventdate, text, link, type_, check=False):
    """Adds new article to db"""
    if check: # Check if event already exists

        cur.execute("select 1 from news where description=%s and organization=%s",
                    [text, organization])

        if cur.fetchone() != None:
            return False

    cur.execute("insert into news (picture, organization, eventdate, description, link, contenttype) values (%s,%s,%s,%s,%s,%s);",
                [picture, organization, eventdate, text, link, type_])

    conn.commit()

    return True

def get_news():
    """Gets all news from db"""
    if not LOCAL:

        cur.execute("select * from news")

        for news in cur.fetchall():

            yield news

def get_news_orgs():
    """Lists organizations which have news"""
    if not LOCAL:

        cur.execute('select distinct organization from news')

        for org in cur.fetchall():

            yield org[0]
