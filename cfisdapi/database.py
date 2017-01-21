
from cfisdapi import app

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

except:
    print "Running without a database..."


def set_grade(user, subject, name, grade, grade_level):
    try:
        cur.execute("SELECT 1 FROM grades WHERE user_id=%s AND name=%s AND subject=%s;",
                    [user, name, subject])
        if cur.fetchone() == None:
            cur.execute("INSERT INTO grades (user_id, name, subject, grade, gradelevel) values (%s,%s,%s,%s,%s);", [
                user, name, subject, grade, grade_level])
        else:
            cur.execute("UPDATE grades SET grade=%s WHERE user_id=%s AND name=%s AND subject=%s;", [
                grade, user, name, subject])
    except:
        print "set_grade error"


def add_news(icon, picture, organization, eventdate, text, link, check=False):
    try:
        if check:
            cur.execute("select 1 from news where description=%s and organization=%s",
                        [text, organization])
            if cur.fetchone() != None:
                return False

        cur.execute("insert into news (icon, picture, organization, eventdate, description, link) values (%s,%s,%s,%s,%s,%s);", [
                    icon, picture, organization, eventdate, text, link])
        conn.commit()
        return True
    except:
        print "add_news error"


def execute(*args):
    try:
        return cur.execute(*args)
    except:
        print "execute error"
        return None


def fetchone():
    try:
        return cur.fetchone()
    except:
        print "fetch error"
        return []


def fetchall():
    try:
        return cur.fetchall()
    except:
        print "fetch error"
        return []
