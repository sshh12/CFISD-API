from flask import Flask

app = Flask(__name__)

import cfisdapi.schedules
import cfisdapi.database
import cfisdapi.faculty
import cfisdapi.grades
import cfisdapi.news


@app.route("/")
def index_page():
    """Returns basic index page."""
    return "Hi! This is the Unoffical CyRanch Api, for info email: shrivu1122@gmail.com"


@app.after_request
def after_request(response):
    """
	Appends every request with allow-origin header.

	This allows for the api to be used directly from javascript
	without cross-origin security issues/exceptions locally e.g. fetch() and ajax.
	"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
