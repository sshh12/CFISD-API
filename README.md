# CFISD API

The python backend for the Cy-Ranch App and the CFISD App.

[Live Code](https://cfisdapi.herokuapp.com/)

## Key Dependencies

* [Flask](http://flask.pocoo.org/)
* [Requests](http://docs.python-requests.org/en/master/)
* [psycopg2](http://initd.org/psycopg/)
* [lxml](http://lxml.de/)

## API

##### GET /api/news/{ school }/all
Returns all news
```js
{
  "news": {
    "all": [
      {
        "date": "January 01, 2000",
        "image": "",
        "link": "#",
        "organization": "The Cy-Ranch App",
        "text": "This is a test.",
        "type": 2
      },
      ...
    ]
  }
}
```

##### GET /api/faculty[?url=http://link/to/webpages/]
Returns a list of all teachers.
```js
{
  "A": [ // Last Name Letter
    {
      "website": "https://sites.google.com/path/to/site",
      "name": "Last, First",
      "email": "email@cfisd.net"
    },
    ...
  ],
  ...
}
```

##### POST password -> /api/current/{ student id }
Returns current grades and classwork for student
```js
{
  "grades": [
    {
      "name": "Honors Class",
      "honors": true,
      "letter": "A",
      "overallavg": "100.00%",
      "categories": {
        "Major Grades": {
          "weight": 0.4,
          "letter": "A",
          "grade": "100.00%"
        },
        ...
      },
      "assignments": [
        {
          "name": "A Class Assignment",
          "date": "MM/DD/YYYY",
          "datedue": "MM/DD/YYYY",
          "gradetype": "Major Grades",
          "letter": "A",
          "grade": "100.00%"
        },
        ...
      ]
    },
    ...
  ],
  "status": "success"
}
```

##### POST password -> /api/reportcard/{ student id }
Returns reportcard for student
```js
{
  "reportcard": [
    {
      "name": "A Class",
      "exams": [
        {
          "average": 100.0,
          "letter": "A"
        },
        ...
      ],
      "semesters": [
        {
          "average": 100.0,
          "letter": "A"
        },
        ...
      ],
      "teacher": "Last, First",
      "room": "4231",
      "averages": [
        {
          "average": 100,
          "letter": "A"
        },
        ...
      ]
    },
    ...
  ],
  "status": "success"
}
```

##### POST password -> /api/transcript/{ student id }
Returns transcript for student
```js
{
  "gpa": {
    "value": 4.0,
    "rank": 50,
    "class_size": 1000
  },
  "status": "success"
}
```

##### POST password -> /api/attendance/{ student id }
Returns attendance info for student
```js
{
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
        },
        ...
      ]
    },
    ...
  ]
}
```

## Tests

```shell
python -m tests.manual
```
