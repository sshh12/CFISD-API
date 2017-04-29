# CyRanch App Server

The python backend for the Cy-Ranch App.

## Key Dependencies

* [Flask](http://flask.pocoo.org/)
* [Requests](http://docs.python-requests.org/en/master/)
* [ujson](https://pypi.python.org/pypi/ujson)
* [psycopg2](http://initd.org/psycopg/)
* [lxml](http://lxml.de/)

## API

##### GET /news/{Organization}
Returns the news for an organization
```js
[  
   {  
      "date":"January 01, 2017",
      "organization":"Organization",
      "text":"News Text",
      "icon":"/local/path/to/icon",
      "image":"http://example.com/link/to/image",
      "link":"http://example.com/article",
      "type":1 // Type Enum: BASIC, ARTICLE, TEXTONLY
   },
   ...
]
```

##### GET /news/list
Returns the all the current news sources and icons
```js
{  
   "Organization":"/local/path/to/icon",
   ...
}
```

##### GET /faculty
Returns a list of all teachers at Cy-Ranch
```js
{  
   "A":[  // Last Name Letter
      {  
         "website":"https://sites.google.com/path/to/site",
         "name":"Last, First",
         "email":"email@cfisd.net"
      },
      ...
   ],
   ...
}
```

##### POST password -> /homeaccess/classwork/{Student ID}
Returns current grades and classwork for student
```js
{  
   "12345 - 6":{  
      "name":"Honors Class",
      "honors":true,
      "letter":"A",
      "overallavg":"100.00%",
      "categories":{  
         "Major Grades":{  
            "weight":0.4,
            "letter":"A",
            "grade":"100.00%"
         },
         ...
      },
      "assignments":{  
         "A Class Assignment":{  
            "date":"MM/DD/YYYY",
            "datedue":"MM/DD/YYYY",
            "gradetype":"Major Grades",
            "letter":"A",
            "grade":"100.00%"
         },
		 ...
      }
   },
   ...
   "status":"success"
}
```

##### POST password -> /homeaccess/reportcard/{Student ID}
Returns reportcard for student
```js
{
   "12345 - 6":{  
      "name":"A Class",
      "exams":[  
         {  
            "average":100.0,
            "letter":"A"
         },
         ...
      ],
      "semesters":[  
         {  
            "average":100.0,
            "letter":"A"
         },
         ...
      ],
      "teacher":"Last, First",
      "room":"4231",
      "averages":[  
         {  
            "average":100,
            "letter":"A"
         },
         ...
      ]
   },
   ...
   "status":"success"
}
```

##### GET /homeaccess/statistics/{Class}/{Assignment}/{Grade}
Returns statistics for a given assignment based on grade specified
```js
{  
   "average":80.0, // Average of All Users
   "percentile":95.0 // % of students below {grade}
}
```

##### GET /schedule
Returns the current school schedule (if abnormal on given day)
```js
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
```

## Tests

```shell
python -m tests.unit -v

python -m tests.manual
```
