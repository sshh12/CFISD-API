from flask import request, jsonify
from urllib.parse import unquote
from lru import LRUCacheDict

import hashlib
import time

from cfisdapi import app
from cfisdapi.homeaccess import HomeAccessCenterUser
import cfisdapi.demo


MAX_CACHE_SIZE = 1024


# create a key for cache dicts
# creates hash(user + pass) to quickly verify users
def get_cache_key(sid, passw):
    m = hashlib.sha256()
    m.update(bytes(sid, 'utf-8'))
    m.update(bytes(passw, 'utf-8'))
    return m.digest()


# caches to speed up repeated requests
cache_settings = dict(max_size=MAX_CACHE_SIZE, concurrent=True)
demo_cache = LRUCacheDict(expiration=60*60*24*365, **cache_settings)   # 1 year (this never needs to update)
current_cache = LRUCacheDict(expiration=60*15, **cache_settings)       # 15 mins
reportcard_cache = LRUCacheDict(expiration=60*60*24, **cache_settings) # 1 day
transcript_cache = LRUCacheDict(expiration=60*60*24, **cache_settings) # 1 day
attendance_cache = LRUCacheDict(expiration=60*60, **cache_settings)    # 1 hour


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

    start_time = time.time()
    hac_user = HomeAccessCenterUser(user)

    cache_key = get_cache_key(hac_user.sid, passw)
    if cache_key in current_cache:
        return current_cache[cache_key]

    if hac_user.login(passw):
        grades = hac_user.get_classwork()
        if hac_user.sid not in demo_cache:
            app.logger.info("Demo({0}) not found...downloading.".format(hac_user.sid))
            hac_user.get_demo()
            demo_cache[hac_user.sid] = True
    else:
        grades = {'status': 'login_failed'}

    app.logger.info("Classwork({0}) found in {1:.2f}s".format(hac_user.sid, time.time() - start_time))

    json_results = jsonify(grades)

    if grades['status'] == 'success':
        current_cache[cache_key] = json_results

    return json_results


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

    start_time = time.time()
    hac_user = HomeAccessCenterUser(user)

    cache_key = get_cache_key(hac_user.sid, passw)
    if cache_key in reportcard_cache:
        return reportcard_cache[cache_key]

    if hac_user.login(passw):
        reportcard = hac_user.get_reportcard()
    else:
        reportcard = {'status': 'login_failed'}

    app.logger.info("Reportcard({0}) found in {1:.2f}s".format(hac_user.sid, time.time() - start_time))

    json_results = jsonify(reportcard)

    if reportcard['status'] == 'success':
        reportcard_cache[cache_key] = json_results

    return json_results


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

    start_time = time.time()
    hac_user = HomeAccessCenterUser(user)

    cache_key = get_cache_key(hac_user.sid, passw)
    if cache_key in transcript_cache:
        return transcript_cache[cache_key]

    if hac_user.login(passw):
        transcript = hac_user.get_transcript()
    else:
        transcript = {'status': 'login_failed'}

    app.logger.info("Transcript({0}) found in {1:.2f}s".format(hac_user.sid, time.time() - start_time))

    json_results = jsonify(transcript)

    if transcript['status'] == 'success':
        transcript_cache[cache_key] = json_results

    return json_results


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

    start_time = time.time()
    hac_user = HomeAccessCenterUser(user)

    cache_key = get_cache_key(hac_user.sid, passw)
    if cache_key in attendance_cache:
        return attendance_cache[cache_key]

    if hac_user.login(passw):
        attendance = hac_user.get_attendance()
    else:
        attendance = {'status': 'login_failed'}

    app.logger.info("Attendance({0}) found in {1:.2f}s".format(hac_user.sid, time.time() - start_time))

    json_results = jsonify(attendance)

    if attendance['status'] == 'success':
        attendance_cache[cache_key] = json_results

    return json_results
