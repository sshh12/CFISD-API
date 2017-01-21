import urlparse
import os

from cfisdapi import app

LOCAL = False

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
    print e
    LOCAL = True


def set_grade(user, subject, name, grade, grade_level):
    if not LOCAL:
        cur.execute("SELECT 1 FROM grades WHERE user_id=%s AND name=%s AND subject=%s;",
                    [user, name, subject])
        if cur.fetchone() == None:
            cur.execute("INSERT INTO grades (user_id, name, subject, grade, gradelevel) values (%s,%s,%s,%s,%s);", [
                user, name, subject, grade, grade_level])
        else:
            cur.execute("UPDATE grades SET grade=%s WHERE user_id=%s AND name=%s AND subject=%s;", [
                grade, user, name, subject])
        return True
    return False


def add_news(icon, picture, organization, eventdate, text, link, check=False):
    if not LOCAL:
        if check:
            cur.execute("select 1 from news where description=%s and organization=%s",
                        [text, organization])
            if cur.fetchone() != None:
                return False

        cur.execute("insert into news (icon, picture, organization, eventdate, description, link) values (%s,%s,%s,%s,%s,%s);", [
                    icon, picture, organization, eventdate, text, link])
        conn.commit()
        return True
    return False


def execute(*args):
    if not LOCAL:
        cur.execute(*args)
        return True
    else:
        return None


def fetchone():
    if not LOCAL:
        return cur.fetchone()
    else:
        return []


def fetchall():
    if not LOCAL:
        return cur.fetchall()
    else:
        return []
