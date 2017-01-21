from cfisdapi import app

FACULTY_FILE = 'faculty.json'


@app.route("/faculty")
def get_faculty():
    with open(FACULTY_FILE, 'r') as ff:
        return ff.read()

# Old Code Used For Parsing Original Site -> faculty.json
#
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
#     return "Done!"
