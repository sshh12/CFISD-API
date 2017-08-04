from cfisdapi import app

special_schedule = """
[
  "Z, Finals Schedule",
  [
    new timeslot("7:30-9:15", "Morning Final"),
    new timeslot("9:21-10:14", "3rd"),
    new timeslot("12:48-14:40", "Afternoon Final")
  ],
  {
    "none": [new timeslot("10:14-12:42", "4th, 5th, Lunch")],
    "a": [
      new timeslot("10:14-10:44", "A Lunch"),
      new timeslot("10:50-11:43", "4th"),
      new timeslot("11:49-12:42", "5th")
    ],
    "b": [
      new timeslot("10:20-11:13", "4th"),
      new timeslot("11:13-11:43", "B Lunch"),
      new timeslot("11:49-12:42", "5th")
    ],
    "c": [
      new timeslot("10:20-11:13", "4th"),
      new timeslot("11:13-12:12", "5th"),
      new timeslot("12:12-12:42", "C Lunch")
    ]
  }
]
"""


@app.route("/schedule")
def get_schedule():
    """
    Returns the schedule if different from A, B, or Pep Rally.

    If the schedule of a given day is abnormal this method will
    return a js object (json) that can be directly eval()'d in the
    mobile app.

    Note
    ----
    Currently toggled manually with code updates...
    """
    if False:  # TODO Allow for remote updating of schedules
        return special_schedule
    return ""
