from flask import Flask

app = Flask(__name__)

import cfisdapi.database
import cfisdapi.faculty
import cfisdapi.schedules
import cfisdapi.news
import cfisdapi.grades


@app.route("/")
def index_page():  # Super Basic index page
    return "Hi! This is the Unoffical CyRanch Api, for info email: shrivu1122@gmail.com"


@app.after_request  # For Allowing Access to JS Clients using fetch()
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
