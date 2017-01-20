from requests import Session, get
from flask import Flask, Response, request
from urllib import unquote
import time
import os
import psycopg2
import urlparse

import ujson
import re

app = Flask(__name__)

FACULTY_FILE = 'faculty.json'

LOCAL = False

if not LOCAL:
    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(os.environ["DATABASE_URL"])
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    cur = conn.cursor()


def sudo_hash(s):  # Delete Me
    return "".join(reversed(map(lambda c: chr(ord(c) % 26 + 65), s.encode('base64').encode('hex'))[:12])).encode('base64')[:12]


class HomeAccessCenter:

    re_get_classes = re.compile(
        "<div class=\"AssignmentClass\">[\S\s]+?<\/span>\s+<\/div>\s+<\/span>")
    re_get_classname = re.compile(
        "(\d+ - \d+)\s{3,4}([\w\s/-]+)\r\n")
    re_get_classavg = re.compile(
        "\"Average of all marking period scores\">(.+)<\/span>")
    re_get_assignments = re.compile(
        "<tr class=\"sg-asp-table-data-row\">[\s\S]+?<\/tr>")
    re_get_assign_name = re.compile(
        "; return false;\">\s+([\S\s]+\S)\s+<\/a>")
    re_get_assign_dates = re.compile(
        "<td>(\d{2}\/\d{2}\/\d{4})<\/td>\s*<td>(\d{2}\/\d{2}\/\d{4})<\/td>")
    re_get_assign_value = re.compile(
        "<td>([\w\s]{11,12})<\/td>[\s\S]+?<td class=\"sg-view-quick\">([\S]+?)<\/td>\s+<\/tr>")
    re_get_reportcard = re.compile(
        r'<tr class="sg-asp-table-data-row">\s+<td>(\d+ - \d+)\s+<\/td><td>\s+<a [\s\w="#(\');]+>([\w\s/\-&]+)<\/a>[\s\w<\/>=":.@]+">([\w\s,]+)<\/a><\/td><td>([\d\w]+)\s*<\/td><td>\s+[\d\.\s<\/td>]+a\s+href="#" onclick="\w+\(\'\d+\', \'\d+\', \'\d\', \'MP1\s+\', \'\w+\', \d+\); return false;">\s+(\d+|\s+)<\/a>[\d\.\s<\/td>]+a\s+href="#" onclick="\w+\(\'\d+\', \'\d+\', \'\d\', \'MP2\s+\', \'\w+\', \d+\); return false;">\s+(\d+|\s+)<\/a>[\d\.\s<\/td>]+a\s+href="#" onclick="\w+\(\'\d+\', \'\d+\', \'\d\', \'MP3\s+\', \'\w+\', \d+\); return false;">\s+(\d+|\s)<\/a>[\s<\/td>a\w;"]+="#"\s+onclick="\w+\(\'\d+\', \'\d+\', \'\d\', \'MP4\s+\', \'\w+\', \d+\); return false;">(\d+|\s+)<\/a>[\s<\/td>a\w;"]+="#"\s+onclick="\w+\(\'\d+\', \'\d+\', \'\d\', \'MP5\s+\', \'\w+\', \d+\); return false;">(\d+|\s+)<\/a>[\s<\/td>a\w;"]+="#"\s+onclick="\w+\(\'\d+\', \'\d+\', \'\d\', \'MP6\s+\', \'\w+\', \d+\); return false;">(\d+|\s+)<\/a>')

    def __init__(self, sid):
        self.sid = sid
        self.session = Session()

    def login(self, password):
        self.passwd = password

        data = {'action': 'login',
                'Database': '10',
                'LogOnDetails.UserName': self.sid,
                'LogOnDetails.Password': self.passwd}

        self.session.post("https://home-access.cfisd.net/HomeAccess/Account/LogOn", data=data)

    def logout(self):
        self.session.get("https://home-access.cfisd.net/HomeAccess/Account/LogOff")

    def _percent_to_float(self, s):
        try:
            return float(s.replace("%", ""))
        except:
            return 0.0

    def _get_letter_grade(self, percent):
        num = self._percent_to_float(percent)
        if num >= 89.5:
            return "A"
        if num >= 79.5:
            return "B"
        if num >= 69.5:
            return "C"
        if num >= 15:
            return "D"
        return "F"

    def get_classwork(self):
        page = self.session.get(
            "https://home-access.cfisd.net/HomeAccess/Content/Student/Assignments.aspx").text

        classwork = {}

        for c in self.re_get_classes.finditer(page):
            try:
                classtext = c.group(0)

                class_id, classname = self.re_get_classname.findall(classtext)[0]
                class_average = self.re_get_classavg.search(
                    classtext).group(1).replace("Marking Period Avg ", "")

                classwork.update({class_id: {'name': classname, 'overallavg': class_average,
                                             'assignments': {}, 'letter': self._get_letter_grade(class_average)}})

                sql_set_grade(self.sid, classname, classname + " AVG",
                              self._percent_to_float(class_average), 25)

                for a in self.re_get_assignments.finditer(classtext):
                    try:
                        assigntext = a.group(0)

                        if self.re_get_assign_name.search(assigntext):

                            assign_name = self.re_get_assign_name.search(assigntext).group(
                                1).replace("&nbsp;", "").replace("&amp;", "&")

                            try:
                                date, datedue = self.re_get_assign_dates.findall(assigntext)[0]
                            except Exception as e:
                                print "Date Error"
                                date, datedue = "1/1/2016", "1/1/2016"

                            datedue = datedue.replace("\\", "")
                            date = date.replace("\\", "")

                            grade_type, grade = self.re_get_assign_value.findall(assigntext)[0]
                            grade = grade.replace("&nbsp;", "")

                            classwork[class_id]['assignments'].update({assign_name: {
                                'date': date,
                                'datedue': datedue,
                                'gradetype': grade_type,
                                'grade': grade,
                                'letter': self._get_letter_grade(grade)}})
                            sql_set_grade(self.sid, classname, assign_name,
                                          self._percent_to_float(grade), 25)
                    except Exception as e:
                        print "Error 1,", str(e)
            except Exception as e:
                print "Error 0, ", str(e)

        return classwork

    def get_reportcard(self):
        page = self.session.get(
            "https://home-access.cfisd.net/HomeAccess/Content/Student/ReportCards.aspx").text

        reportcard = {}

        for r in self.re_get_reportcard.finditer(page):
            classid = r.group(1)
            classname = r.group(2)
            teacher = r.group(3)
            room = r.group(4)
            averages = {}
            for i in range(6):
                avg = r.group(i + 5).strip()
                averages.update({i: {'average': avg,
                                     'letter': self._get_letter_grade(avg)}})

            reportcard.update({classid: {'name': classname,
                                         'teacher': teacher,
                                         'room': room,
                                         'averages': averages}})

        return reportcard


def sql_set_grade(user, subject, name, grade, grade_level):
    cur.execute("SELECT 1 FROM grades WHERE user_id=%s AND name=%s AND subject=%s;",
                [user, name, subject])
    if cur.fetchone() == None:
        cur.execute("INSERT INTO grades (user_id, name, subject, grade, gradelevel) values (%s,%s,%s,%s,%s);", [
                    user, name, subject, grade, grade_level])
    else:
        cur.execute("UPDATE grades SET grade=%s WHERE user_id=%s AND name=%s AND subject=%s;", [
                    grade, user, name, subject])


@app.route("/homeaccess/classwork/<user>", methods=['POST'])
def get_classwork(user=""):
    try:
        passw = unquote(request.form['password'])

        t = time.time()
        u = HomeAccessCenter(user)
        u.login(passw)
        grades = u.get_classwork()

        print "GOT Grades For {} in {}".format(user, time.time() - t)

        return ujson.dumps(grades)
    except Exception as e:
        print str(e)
        return "ERROR"


@app.route("/homeaccess/reportcard/<user>", methods=['POST'])
def get_reportcard(user=""):
    try:
        passw = unquote(request.form['password'])

        t = time.time()
        u = HomeAccessCenter(user)
        u.login(passw)
        reportcard = u.get_reportcard()

        print "GOT ReportCard For {} in {}".format(user, time.time() - t)

        return ujson.dumps(reportcard)
    except Exception as e:
        print str(e)
        return "ERROR"


@app.route("/homeaccess/stats/<subject>/<name>/<grade>")
def homeaccess_stats(subject="", name="", grade="0.0"):
    try:
        grade = float(grade)

        cur.execute("SELECT AVG(grade) FROM grades WHERE name=%s AND subject=%s;", [name, subject])
        avg = cur.fetchone()[0]

        #cur.execute("SELECT median(grade) FROM grades WHERE name=%s AND subject=%s;", [name, subject])
        #median = cur.fetchone()[0]

        cur.execute("SELECT COUNT(grade) FROM grades WHERE name=%s AND subject=%s;",
                    [name, subject])
        total_grades = cur.fetchone()[0]

        cur.execute("SELECT COUNT(grade) FROM grades WHERE name=%s AND subject=%s AND grade <= %s;", [
                    name, subject, grade])
        below_grades = cur.fetchone()[0]

        percent = min(below_grades / float(total_grades - 1) * 100.0, 99.99)

        return ujson.dumps({'Average': avg, 'PercentBelow': percent})
    except Exception as e:
        print(e)
    return "error"

# Schedule
special_schedule = """
[
  "Z, Finals Schedule",
  [
    new timeslot("7:30-9:15", "Morning Final"),
    new timeslot("9:21-10:14", "3rd"),
    new timeslot("12:48-14:40", "Afternoon Final")
  ],
  {
    "none": [new timeslot("10:14-12:42", "4th, 5th, Lunch")],
    "a": [
      new timeslot("10:14-10:44", "A Lunch"),
      new timeslot("10:50-11:43", "4th"),
      new timeslot("11:49-12:42", "5th")
    ],
    "b": [
      new timeslot("10:20-11:13", "4th"),
      new timeslot("11:13-11:43", "B Lunch"),
      new timeslot("11:49-12:42", "5th")
    ],
    "c": [
      new timeslot("10:20-11:13", "4th"),
      new timeslot("11:13-12:12", "5th"),
      new timeslot("12:12-12:42", "C Lunch")
    ]
  }
]
"""


@app.route("/schedule")
def get_schedule():
    if False and len(special_schedule) > 10:
        return special_schedule
    return ""


# Faculty
@app.route("/faculty")
def faculty():
    with open(FACULTY_FILE, 'r') as f:
        faculty = f.read()
    return faculty


# def update_faculty():
#     teachers = {}
#
#     soup = BeautifulSoup(get("https://app.cfisd.net/urlcap/campus_list_012.html").text, "lxml")
#     current_letter = ""
#
#     for item in soup.find_all('span'):
#         if "arhev" in item.get('class'):
#             try:
#                 if(len(item.string) == 1):
#                     teachers.update({item.string: []})
#                     current_letter = str(item.string)
#             except:
#                 contents, length = item.contents, len(item.contents)
#                 name = None
#
#                 if length == 3:
#                     name = str(clean_string(contents[0]))
#                     website = "none"
#                     email = str(contents[1]["href"].replace("mailto:", ""))
#
#                 elif length == 6:
#                     name = str(clean_string(contents[1].string))
#                     email = str(contents[4]["href"].replace("mailto:", ""))
#                     website = str(contents[1]["href"])
#
#                     if name:
#                         index = len(teachers[current_letter])
#                         teachers[current_letter].append(
#                             {"name": name,
#                              "email": email,
#                              "website": website})
#     del soup
#
#     with open(FACULTY_FILE, 'w') as f:
#         f.write(json.dumps(teachers, indent=3))
#
#     del teachers
#
    # return "Done!"

# News
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
            text = get("http://cyranchnews.com/category" + url).text
            for a in re_get_cyranch_article.finditer(text):
                add_news("/icons/CyRanchMustangs.png", a.group(2), category, a.group(4),
                         a.group(3).replace("&#8217;", "'"), a.group(1), check=True)


def add_news(icon, picture, organization, eventdate, text, link, check=False):
    if check:
        cur.execute("select 1 from news where description=%s and organization=%s",
                    [text, organization])
        if cur.fetchone() != None:
            return False

    cur.execute("insert into news (icon, picture, organization, eventdate, description, link) values (%s,%s,%s,%s,%s,%s);", [
                icon, picture, organization, eventdate, text, link])
    conn.commit()
    return True


@app.route("/news/<org>")
def get_org_news(org=""):

    global cyranch_news_last
    if time.time() - cyranch_news_last > 86400:
        cyranch_news_last = time.time()
        update_cyranch_news()

    news = []
    cur.execute("select * from news where organization=%s", [org])
    for n in cur.fetchall():
        news.append({
                    'date': n[4].strftime("%B %d, %Y"),
                    'image': n[2],
                    'icon': n[1],
                    'organization': n[3],
                    'text': n[5],
                    'link': n[6]
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

        cur.execute("select distinct icon from news where organization=%s", ['The Cy-Ranch App'])
        icon = cur.fetchone()[0]

        if sudo_hash(org) == password:
            add_news(icon, pic, org, date, text, link)
            return "DONE"
        return "Error"

    else:
        orgs = []

        cur.execute("select distinct organization from news")
        for org in cur.fetchall():
            orgs.append(org[0])

        return form_html.replace("OPTIONS",
                                 "\n".join(map(lambda s: "<option value=\"{}\">{}</option>".format(s, s), orgs)))


@app.route("/news/list")
def list_news():
    orgs = {}
    cur.execute("select distinct organization, icon from news")
    for org in cur.fetchall():
        orgs.update({org[0]: org[1]})
    return ujson.dumps(orgs)


# Index
@app.route("/")
def index_page():
    return "Hi! This is the Unoffical CFISD/CyRanch Api, for info email: shrivu1122@gmail.com"


# Allows for JS to fetch() page
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
