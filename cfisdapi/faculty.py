from cfisdapi import app

FACULTY_FILE = 'faculty.json'

@app.route("/faculty")
def get_faculty():
    """Returns (static) json of school faculty."""
    with open(FACULTY_FILE, 'r') as ff:
        return ff.read()
