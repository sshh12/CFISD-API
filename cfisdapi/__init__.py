from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

import cfisdapi.schedules
import cfisdapi.database
import cfisdapi.faculty
import cfisdapi.grades
import cfisdapi.news

import cfisdapi.grades_dep
import cfisdapi.news_dep


@app.route("/")
def index_page():
    """Returns basic index page."""
    return "Hi! This is the Unoffical CyRanch Api, for info email: shrivu1122@gmail.com"

@app.route("/ping")
def test_page():
    """Checks connection to server."""
    return "pong"
