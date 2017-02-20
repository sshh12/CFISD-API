from requests import Session
from flask import request
from urllib import unquote
import re
import time
import ujson

from cfisdapi import app
from cfisdapi.database import set_grade, execute, fetchone, fetchall


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

    re_honors = re.compile(
        r'\b(?:AP|K)\b')

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
                    "https://home-access.cfisd.net/HomeAccess/Content/Student/Assignments.aspx").text
            except:
                return {'status': 'connection_failed'}

        classwork = {}

        for c in self.re_get_classes.finditer(page):
            try:
                classtext = c.group(0)

                class_id, classname = self.re_get_classname.findall(classtext)[0]

                class_average = self.re_get_classavg.search(classtext).group(1)
                class_average = class_average.replace("Marking Period Avg ", "")

                honors = self._is_honors(classname)

                classwork.update({class_id: {'name': classname,
                                             'honors': honors,
                                             'overallavg': class_average,
                                             'assignments': {},
                                             'letter': self._get_letter_grade(class_average)}})
                
                class_avg = self._percent_to_float(class_average)
                

                for a in self.re_get_assignments.finditer(classtext):
                    try:
                        assigntext = a.group(0)

                        if self.re_get_assign_name.search(assigntext):

                            assign_name = self.re_get_assign_name.search(assigntext).group(1)
                            assign_name = assign_name.replace("&nbsp;", "").replace("&amp;", "&")

                            try:  # Fix
                                date, datedue = self.re_get_assign_dates.findall(assigntext)[0]
                            except Exception as e:
                                date, datedue = "1/1/2016", "1/1/2016"

                            datedue = datedue.replace("\\", "")
                            date = date.replace("\\", "")

                            grade_type, grade = self.re_get_assign_value.findall(assigntext)[0]
                            grade = grade.replace("&nbsp;", "")

                            classwork[class_id]['assignments'].update({
                                assign_name: {
                                    'date': date,
                                    'datedue': datedue,
                                    'gradetype': grade_type,
                                    'grade': grade,
                                    'letter': self._get_letter_grade(grade)}})
                            
                            assign_avg = self._percent_to_float(grade)
                            if assign_avg > 10:
                                set_grade(self.sid,
                                          classname,
                                          assign_name,
                                          assign_avg,
                                          25)
                                
                    except Exception as e:
                        print "Error 1,", str(e) # Fix

                    if class_avg > 10:
                        set_grade(self.sid,
                                  classname,
                                  classname + " AVG",
                                  class_avg,
                                  25)
                    
            except Exception as e:
                print "Error 0, ", str(e) # Fix

        classwork.update({'status': 'success'})

        return classwork

    def get_reportcard(self, page=None):
        if not page:
            try:
                page = self.session.get(
                    "https://home-access.cfisd.net/HomeAccess/Content/Student/ReportCards.aspx").text
            except:
                return {'status': 'connection_failed'}

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
                                         'teacher': teacher.title(),
                                         'room': room,
                                         'averages': averages}})

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
