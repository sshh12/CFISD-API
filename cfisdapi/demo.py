"""
Sample responses for test user `s000000`
"""

CLASSWORK = {
  "grades": [
    {
      "name": "Honors Class",
      "honors": True,
      "letter": "A",
      "overallavg": "100.00%",
      "categories": {
        "Major Grades": {
          "weight": 0.4,
          "letter": "A",
          "grade": "100.00%"
        }
      },
      "assignments": [
        {
          "name": "A Class Assignment",
          "date": "MM/DD/YYYY",
          "datedue": "MM/DD/YYYY",
          "gradetype": "Major Grades",
          "letter": "A",
          "grade": "100.00%"
        }
      ]
    }
  ],
  "status": "success"
}

REPORTCARD = {
  "reportcard": [
    {
      "name": "A Class",
      "exams": [
        {
          "average": 100.0,
          "letter": "A"
        }
      ],
      "semesters": [
        {
          "average": 100.0,
          "letter": "A"
        }
      ],
      "teacher": "Last, First",
      "room": "4231",
      "averages": [
        {
          "average": 100,
          "letter": "A"
        }
      ]
    }
  ],
  "status": "success"
}

TRANSCRIPT = {
  "gpa": {
    "value": 4.0,
    "rank": 50,
    "class_size": 1000
  },
  "status": "success"
}

ATTENDANCE = {
  "months": [
    {
      "name": "May 2018",
      "timestamp": 1525150800.0,
      "days": [
        {
          "day": 1,
          "timestamp": 1525150800.0,
          "info": {
            "1": "Field Trip Instructional",
            "2": "Field Trip Instructional"
          }
        }
      ]
    }
  ]
}
