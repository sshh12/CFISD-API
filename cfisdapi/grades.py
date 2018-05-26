from requests import Session, Timeout
from flask import request, jsonify
from urllib.parse import unquote
from datetime import datetime
from lxml import html
import time
import re

from cfisdapi import app
from cfisdapi.database import set_grade, add_user, add_rank, is_user

HAC_SERVER_TIMEOUT = 15

class HomeAccessCenterUser:
    """Represents an instance of a Home Access Center user"""

    re_honors = re.compile(r'\b(?:AP|K)\b')

    def __init__(self, sid):
        """
        Constructor.

        Parameters
        ----------
        sid : str
            The student id of the user
        """
        self.sid = sid
        self.session = Session()

    def login(self, password):
        """
        Sends a login request and validates credentials

        Parameters
        ----------
        password : str
            The users password
        """
        self.passwd = password

        if self.sid == 's000000': # Test Account
            return True

        data = {'action': 'login',
                'Database': '10',
                'LogOnDetails.UserName': self.sid,
                'LogOnDetails.Password': self.passwd}

        try:
            resp = self.session.post(
                "https://home-access.cfisd.net/HomeAccess/Account/LogOn", timeout=HAC_SERVER_TIMEOUT, data=data)
        except:
            return False

        if "Logoff" in resp.text:  # Test If Login Worked
            return True

        return False

    def logout(self):  # Ignored to Keep Resp. Times Lower
        """Logout the user and devalidate cookies"""
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
        elif num >= 79.5:
            return 'B'
        elif num >= 69.5:
            return 'C'
        elif num >= 15:
            return 'D'
        elif num < 1:
            return 'Z'
        else:
            return 'F'

    def _is_honors(self, name):
        return name != '' and self.re_honors.search(name) != None

    def get_classwork(self, page=None):
        """
        Gets the users current classwork for the six weeks

        Parameters
        ----------
        page : str
            A string representing an html page containing raw grades webpage html

        Returns
        -------
        Dict containing classwork
        """
        if not page:

            if self.sid == 's000000': # Test User

                with open("tests/data/classwork_5-24-2017.html", 'r') as dat:
                    page = dat.read()

            else:

                try:

                    page = self.session.get("https://home-access.cfisd.net/HomeAccess/Content/Student/Assignments.aspx", timeout=HAC_SERVER_TIMEOUT).content

                except Timeout:

                    return {'status': 'connection_failed'}

        tree = html.fromstring(page)

        classwork = []

        try:

            for class_ in tree.find_class('AssignmentClass'):

                class_id, classname = ([s.strip() for s in class_.find_class('sg-header-heading')[0].text_content().split(" " * 3) if s != ""])[1:3]

                class_average = class_.find_class('sg-header-heading sg-right')[0].text_content().split(' ')[-1]

                class_avg_asfloat = self._percent_to_float(class_average)

                classwork.append({
                                  'name': classname,
                                  'honors': self._is_honors(classname),
                                  'overallavg': class_average,
                                  'assignments': [],
                                  'categories': [],
                                  'letter': self._get_letter_grade(class_average)
                                 })

                if class_avg_asfloat > 10:
                    set_grade(self.sid,
                              classname,
                              classname + " AVG",
                              class_avg_asfloat,
                              "Class")

                for row in class_.find_class('sg-asp-table-data-row'):

                    cols = list(map(lambda el: el.text_content(), row.xpath("td")))

                    if len(cols) == 10:

                        assign_name = cols[2].replace("*", "").strip().replace("&nbsp;", "").replace("&amp;", "&")

                        datedue = cols[0].replace(u'\xa0', "")
                        date = cols[1].replace(u'\xa0', "")

                        grade_type = cols[3]
                        grade = cols[-1].replace("&nbsp;", "").replace(u'\xa0', "")

                        assign_avg_asfloat = self._percent_to_float(grade)

                        classwork[-1]['assignments'].append({
                                                            'name': assign_name,
                                                            'date': date,
                                                            'datedue': datedue,
                                                            'gradetype': grade_type,
                                                            'grade': grade,
                                                            'letter': self._get_letter_grade(grade)
                                                            })

                        if assign_avg_asfloat > 10:
                            set_grade(self.sid,
                                      classname,
                                      assign_name,
                                      assign_avg_asfloat,
                                      grade_type)

                    elif len(cols) == 6:

                        category = cols[0]
                        grade = cols[3].strip()
                        weight = float(cols[4])
                        letter = self._get_letter_grade(grade)

                        classwork[-1]['categories'].append({
                                                            'name': category,
                                                            'grade': grade,
                                                            'weight': weight,
                                                            'letter': letter
                                                           })

        except Exception as e:
            print(str(e) + " -- grades")

        return {'grades': classwork, 'status': 'success'}

    def get_reportcard(self, page=None):
        """
        Gets the users reportcard for the year

        Parameters
        ----------
        page : str
            A string representing an html page containing raw reportcard webpage html

        Returns
        -------
        Dict containing reportcard
        """
        if not page:

            try:

                page = self.session.get("https://home-access.cfisd.net/HomeAccess/Content/Student/ReportCards.aspx", timeout=HAC_SERVER_TIMEOUT).content

            except Timeout:

                return {'status': 'connection_failed'}

        tree = html.fromstring(page)

        reportcard = []

        for row in tree.find_class('sg-asp-table-data-row'):

            cols = list(map(lambda el: el.text_content().strip(), row.xpath("td")))

            classid = cols[0]
            classname = cols[1]
            teacher = cols[3].title()
            room = cols[4]

            averages = []
            for i in [7, 8, 11, 12]:
                averages.append({'average': self._percent_to_float(cols[i]), 'letter': self._get_letter_grade(cols[i])})

            exams = []
            sems = []
            for i in [9, 13]:
                exams.append({'average': self._percent_to_float(cols[i]), 'letter': self._get_letter_grade(cols[i])})
                sems.append({'average': self._percent_to_float(cols[i + 1]), 'letter': self._get_letter_grade(cols[i + 1])})

            reportcard.append({'name': classname,
                               'teacher': teacher,
                               'room': room,
                               'averages': averages,
                               'exams': exams,
                               'semesters': sems})

        return {'reportcard': reportcard, 'status': 'success'}

    def get_transcript(self, page=None):
        """
        Gets transcript info about user

        Parameters
        ----------
        page : str
            A string representing an html page containing raw information webpage html

        Returns
        -------
        Dict containing transcript info

        Note
        ----
        Demo account will return empty dict
        """
        if self.sid == 's000000':
            return {}

        if not page:

            try:

                page = self.session.get("https://home-access.cfisd.net/HomeAccess/Content/Student/Transcript.aspx", timeout=HAC_SERVER_TIMEOUT).content

            except Timeout:

                return {'status': 'connection_failed'}

        tree = html.fromstring(page)

        transcript = {}

        try:

            current_gpa = tree.xpath("//span[@id='plnMain_rpTranscriptGroup_lblGPACum1']")[0].text_content().strip()
            rank = tree.xpath("//span[@id='plnMain_rpTranscriptGroup_lblGPARank1']")[0].text_content().strip().split(' / ')

            transcript.update({
                'gpa': {
                    'value': float(current_gpa),
                    'rank': int(rank[0]),
                    'class_size': int(rank[1])
                },
                'status': 'success'
            })

        except:

            return {'status': 'server_error'}

        add_rank(self.sid, transcript)

        return transcript

    def get_demo(self, page=None):
        """
        Gets demographic info about user

        Parameters
        ----------
        page : str
            A string representing an html page containing raw information webpage html

        Returns
        -------
        Dict containing demographic info

        Note
        ----
        Demo account will return empty dict
        """
        if self.sid == 's000000':
            return {}

        if is_user(self.sid):
            return {'status': 'already_added'}

        if not page:

            try:

                page = self.session.get("https://home-access.cfisd.net/HomeAccess/Content/Student/Registration.aspx", timeout=HAC_SERVER_TIMEOUT).content

            except Timeout:

                return {'status': 'connection_failed'}

        tree = html.fromstring(page)

        demo = {}

        name = tree.xpath("//span[@id='plnMain_lblRegStudentName']")[0].text_content().strip()
        school = tree.xpath("//span[@id='plnMain_lblBuildingName']")[0].text_content().strip().title()
        gender = tree.xpath("//span[@id='plnMain_lblGender']")[0].text_content().strip().lower()
        grade = int(tree.xpath("//span[@id='plnMain_lblGrade']")[0].text_content().strip())
        language = tree.xpath("//span[@id='plnMain_lblLanguage']")[0].text_content().strip().lower()

        demo.update({'name': name,
                     'school': school,
                     'gender': gender,
                     'gradelevel': grade,
                     'language': language})

        add_user(self.sid, demo)

        return demo

    def get_attendance(self):

        attend = {'months': []}

        current_params = True # Required page params

        while current_params: # While there is a page to check

            data = {}

            if type(current_params) == list:

                data = {
                    '__EVENTTARGET': current_params[0],
                    '__EVENTARGUMENT': current_params[1],
                    '__VIEWSTATE': current_params[2],
                    '__VIEWSTATEGENERATOR': current_params[3],
                    '__EVENTVALIDATION': current_params[4]
                }

            page = self.session.post("https://home-access.cfisd.net/HomeAccess/Content/Attendance/MonthlyView.aspx", timeout=HAC_SERVER_TIMEOUT, data=data).content

            tree = html.fromstring(page)

            header = tree.xpath("//table[@class='sg-asp-calendar-header']")[0]

            month = header.text_content().replace(">", "").replace("<", "").strip()

            attend_month = {
                'name': month,
                'timestamp': datetime.strptime(month, "%B %Y").timestamp(),
                'days': []
            }

            try: # Find the "<-" button and get its form attributes

                before_params = header.xpath("//a[@title=\"Go to the previous month\"]")[0].attrib['href'].replace("javascript:__doPostBack('", "").replace("')", "").split("','")

                before_params.append(tree.xpath("//input[@name='__VIEWSTATE']")[0].attrib['value'])
                before_params.append(tree.xpath("//input[@name='__VIEWSTATEGENERATOR']")[0].attrib['value'])
                before_params.append(tree.xpath("//input[@name='__EVENTVALIDATION']")[0].attrib['value'])

            except:

                before_params = None

            rows = tree.xpath("//tr")

            for row_num in range(3, len(rows)): # Parse the calender

                for col in rows[row_num]:

                    if col.text_content().isnumeric():

                        day = int(col.text_content())

                        day_text = str(day).zfill(2) + " " + month

                        attend_day = {
                            'day': day,
                            'timestamp': datetime.strptime(day_text, "%d %B %Y").timestamp()
                        }

                        if 'title' in col.attrib: # has info text

                            attend_info = {}

                            info = col.attrib['title'].strip().split("\r")

                            for i in range(0, len(info) - 1, 2): # 1 A 2 B 3 C -> {1: A, 2: B, 3: C}
                                attend_info[info[i]] = info[i + 1]

                            attend_day['info'] = attend_info

                        attend_month['days'].append(attend_day)

            attend['months'].append(attend_month)

            current_params = before_params

            if "Aug" in month: break # Schools start in Aug so no more data

        attend['status'] = 'success'

        return attend


@app.route("/api/current/<user>", methods=['POST'])
def get_hac_classwork(user=""):
    """
    Classwork

    Parameters
    ----------
    user : str
        Username
    password : str (form)
        Password

    Returns
    -------
    str (json)
        A json formatted compilation of the users latest grades. In the event
        of an error the 'status' attribute will reflect the issue that occured.

    Note
    ----
    Every request will print username and fetch time for debugging.
    """
    passw = unquote(request.get_json()['password'])

    t = time.time()
    u = HomeAccessCenterUser(user)

    if u.login(passw):

        grades = u.get_classwork()
        u.get_demo()

    else:

        grades = {'status': 'login_failed'}

    print("GOT Classwork for {0} in {1:.2f}".format(user, time.time() - t))

    return jsonify(grades)

@app.route("/api/reportcard/<user>", methods=['POST'])
def get_hac_reportcard(user=""):
    """
    Report Card

    Parameters
    ----------
    user : str
        Username
    password : str (form)
        Password

    Returns
    -------
    str (json)
        A json formatted compilation of the users reportcard. In the event
        of an error the 'status' attribute will reflect the issue that occured.

    Note
    ----
    Every request will print username and fetch time for debugging.
    """
    passw = unquote(request.get_json()['password'])

    t = time.time()
    u = HomeAccessCenterUser(user)

    if u.login(passw):

        reportcard = u.get_reportcard()

    else:

        reportcard = {'status': 'login_failed'}

    print("GOT Reportcard for {0} in {1:.2f}".format(user, time.time() - t))

    return jsonify(reportcard)

@app.route("/api/transcript/<user>", methods=['POST'])
def get_hac_transcript(user=""):
    """
    Transcript

    Parameters
    ----------
    user : str
        Username
    password : str (form)
        Password

    Returns
    -------
    str (json)
        A json formatted compilation of the users transcript. In the event
        of an error the 'status' attribute will reflect the issue that occured.

    Note
    ----
    Every request will print username and fetch time for debugging.
    """
    passw = unquote(request.get_json()['password'])

    t = time.time()
    u = HomeAccessCenterUser(user)

    if u.login(passw):

        transcript = u.get_transcript()

    else:

        transcript = {'status': 'login_failed'}

    print("GOT Transcript for {0} in {1:.2f}".format(user, time.time() - t))

    return jsonify(transcript)

@app.route("/api/attendance/<user>", methods=['POST'])
def get_hac_attendance(user=""):
    """
    Attendance

    Parameters
    ----------
    user : str
        Username
    password : str (form)
        Password

    Returns
    -------
    str (json)
        A json formatted compilation of the users attenance records. In the event
        of an error the 'status' attribute will reflect the issue that occured.

    Note
    ----
    Every request will print username and fetch time for debugging.
    """
    passw = unquote(request.get_json()['password'])

    t = time.time()
    u = HomeAccessCenterUser(user)

    if u.login(passw):

        attendance = u.get_attendance()

    else:

        attendance = {'status': 'login_failed'}

    print("GOT Attendance for {0} in {1:.2f}".format(user, time.time() - t))

    return jsonify(attendance)
