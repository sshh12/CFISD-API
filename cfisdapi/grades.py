from requests import Session
from flask import request
from urllib import unquote
from lxml import html
import re
import time
import ujson

from cfisdapi import app
from cfisdapi.database import set_grade, execute, fetchone, fetchall


class HomeAccessCenter:

    re_get_classname = re.compile("(\d+ - \d+)\s{3,4}([\w\s/-]+)\r\n")
    re_honors = re.compile(r'\b(?:AP|K)\b')

    def __init__(self, sid):
        self.sid = sid
        self.session = Session()

    def login(self, password):
        self.passwd = password

        data = {'action': 'login',
                'Database': '10',
                'LogOnDetails.UserName': self.sid,
                'LogOnDetails.Password': self.passwd}

        resp = self.session.post(
            "https://home-access.cfisd.net/HomeAccess/Account/LogOn", data=data)

        if "ViewAssignments" not in resp.text:  # Test If Login Worked
            return False
        return True

    def logout(self):  # Ignored to Keep Resp. Times Lower
        self.session.get("https://home-access.cfisd.net/HomeAccess/Account/LogOff")

    def _percent_to_float(self, s):
        try:
            return float(s.replace("%", ""))
        except ValueError:
            return 0.0

    def _get_letter_grade(self, percent):

        if not percent:
            return ''

        elif 'X' in percent:
            return 'U'

        num = self._percent_to_float(percent)
        if num >= 89.5:
            return 'A'
        if num >= 79.5:
            return 'B'
        if num >= 69.5:
            return 'C'
        if num >= 15:
            return 'D'
        return 'F'

    def _is_honors(self, name):
        return name != '' and self.re_honors.search(name) != None

    def get_classwork(self, page=None):
        if not page:
            try:
                page = self.session.get(
                    "https://home-access.cfisd.net/HomeAccess/Content/Student/Assignments.aspx").content
            except:
                return {'status': 'connection_failed'}

        tree = html.fromstring(page)

        classwork = {}

        for class_ in tree.find_class('AssignmentClass'):

            class_id, classname = self.re_get_classname.findall(class_.find_class('sg-header-heading')[0].text_content())[0]

            class_average = class_.find_class('sg-header-heading sg-right')[0].text_content().split(' ')[-1]

            class_avgf = self._percent_to_float(class_average)

            classwork.update({class_id: {'name': classname,
                                         'honors': self._is_honors(classname),
                                         'overallavg': class_average,
                                         'assignments': {},
                                         'letter': self._get_letter_grade(class_average)}})

            for row in class_.find_class('sg-asp-table-data-row'):
                
                cols = map(lambda el: el.text_content(), row.xpath("td"))
                
                if len(cols) == 10:
                    
                    assign_name = cols[2].replace("\t*", "").strip().replace("&nbsp;", "").replace("&amp;", "&")
                    
                    datedue = cols[0].replace(u'\xa0', "")
                    date = cols[1].replace(u'\xa0', "")

                    grade_type = cols[3]
                    grade = cols[-1].replace("&nbsp;", "").replace(u'\xa0', "")

                    assign_avgf = self._percent_to_float(grade)

                    classwork[class_id]['assignments'].update({
                                                         assign_name: {
                                                            'date': date,
                                                            'datedue': datedue,
                                                            'gradetype': grade_type,
                                                            'grade': grade,
                                                            'letter': self._get_letter_grade(grade)}})
                            
                            
                    if assign_avgf > 10 and False:
                        set_grade(self.sid,
                        classname,
                        assign_name,
                        assign_avgf,
                        25)

            if class_avgf > 10 and False:
                        set_grade(self.sid,
                                  classname,
                                  classname + " AVG",
                                  class_avgf,
                                  25)
        

        classwork.update({'status': 'success'})

        return classwork

    def get_reportcard(self, page=None):
        if not page:
            try:
                page = self.session.get(
                    "https://home-access.cfisd.net/HomeAccess/Content/Student/ReportCards.aspx").content
            except:
                return {'status': 'connection_failed'}

        tree = html.fromstring(page)

        reportcard = {}

        for row in tree.find_class('sg-asp-table-data-row'):

           cols = map(lambda el: el.text_content().strip(), row.xpath("td"))

           classid = cols[0]
           classname = cols[1]
           teacher = cols[3].title()
           room = cols[4]

           averages = []
           for i in [7,8,9,12,13,14]:
               averages.append({'average':self._percent_to_float(cols[i]), 'letter':self._get_letter_grade(cols[i])})

           exams = []
           sems = []
           for i in [10, 15]:
               exams.append({'average':self._percent_to_float(cols[i]), 'letter':self._get_letter_grade(cols[i])})
               sems.append({'average':self._percent_to_float(cols[i+1]), 'letter':self._get_letter_grade(cols[i+1])})

           reportcard.update({classid: {'name': classname,
                                        'teacher': teacher,
                                        'room': room,
                                        'averages': averages,
                                        'exams':exams,
                                        'semesters':sems}})
               

        reportcard.update({'status': 'success'})

        return reportcard


@app.route("/homeaccess/classwork/<user>", methods=['POST'])
def get_classwork(user=""):
    try:
        passw = unquote(request.form['password'])

        t = time.time()
        u = HomeAccessCenter(user)

        if u.login(passw):
            grades = u.get_classwork()
        else:
            grades = {'status': 'login_failed'}

        print "GOT Grades For {} in {}".format(user, time.time() - t)

        return ujson.dumps(grades)
    except Exception as e:
        print str(e)
        return "Error"


@app.route("/homeaccess/reportcard/<user>", methods=['POST'])
def get_reportcard(user=""):
    try:
        passw = unquote(request.form['password'])

        t = time.time()
        u = HomeAccessCenter(user)

        if u.login(passw):
            reportcard = u.get_reportcard()
        else:
            reportcard = {'status': 'login_failed'}

        print "GOT ReportCard For {} in {}".format(user, time.time() - t)

        return ujson.dumps(reportcard)
    except Exception as e:
        print str(e)
        return "Error"


@app.route("/homeaccess/stats/<subject>/<name>/<grade>")
def homeaccess_stats(subject="", name="", grade="0.0"):
    try:
        grade = float(grade)

        execute("SELECT AVG(grade) FROM grades WHERE name=%s AND subject=%s;", [name, subject])
        avg = fetchone()[0]

        #cur.execute("SELECT median(grade) FROM grades WHERE name=%s AND subject=%s;", [name, subject])
        #median = cur.fetchone()[0]

        execute("SELECT COUNT(grade) FROM grades WHERE name=%s AND subject=%s;",
                [name, subject])
        total_grades = fetchone()[0]

        execute("SELECT COUNT(grade) FROM grades WHERE name=%s AND subject=%s AND grade <= %s;", [
            name, subject, grade])
        below_grades = fetchone()[0]

        percentile = min(below_grades / float(total_grades - 1) * 100.0, 99.99)

        return ujson.dumps({'Average': avg, 'PercentBelow': percentile})
    except Exception as e:
        print(e)
    return "Error"
