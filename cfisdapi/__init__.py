from flask import Flask
from flask_cors import CORS
import logging
import sys

app = Flask(__name__)
cors = CORS(app)


class DNSRedirectMiddleware(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        host = environ.get('HTTP_HOST', '')
        uri = environ.get('RAW_URI', '')
        if host == 'cfisdapi.herokuapp.com':
            print('Bad host...redirecting.')
            return start_response('301 MOVED PERMANENTLY', [('location', 'https://cfisdapi.sshh.io' + uri)])(b'')
        return self.app(environ, start_response)


app.wsgi_app = DNSRedirectMiddleware(app.wsgi_app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)


import cfisdapi.database
import cfisdapi.faculty
import cfisdapi.grades
import cfisdapi.news

HOME_TEXT = """
<h4>
<b>Hi!</b>
This is the Unoffical CFISD API.
For help see <a href=\"https://github.com/sshh12/CFISD-API\">github.com/sshh12/CFISD-API</a>
or contact me @ <a href=\"https://sshh.io\">sshh.io</a>
</h4>
"""

@app.route("/")
def index_page():
    """Returns basic index page."""
    return HOME_TEXT

@app.route("/ping")
def test_page():
    """Checks connection to server."""
    return "pong"
