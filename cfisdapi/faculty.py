from cfisdapi import app

from flask import request, jsonify
import requests
import re

@app.route("/api/faculty/list")
def get_faculty():
    """Returns json of school faculty."""

    url = request.args.get('url', default="https://app.cfisd.net/urlcap/campus_list_012.html", type=str)

    teachers = get_faculty_from_url(url)

    return jsonify(teachers)

def get_faculty_from_url(url):

    teachers = {}

    page = requests.get(url).text.replace('&nbsp;', '')

    for text in re.finditer('<span class=\'arhev\'>([\s\S]+?)<\/span>', page):

        user_text = text.group(1)

        if 'mailto:' in user_text:

            name = re.search('\\s*([A-Za-z\\s\\-\']+, [A-Za-z\\s\\-\']+?)\\s*<', user_text).group(1).strip()

            email = re.search('<a href=mailto:(\S+?)>', user_text).group(1)

            website = re.search('target="_blank" href=(\S+?)>', user_text)

            if website:
                website = website.group(1)

            if name[0] not in teachers:
                teachers[name[0]] = []

            teachers[name[0]].append({
                'name': name,
                'email': email,
                'website': website
            })

    return teachers
