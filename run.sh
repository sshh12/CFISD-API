#!/bin/bash
gunicorn --timeout 40 --max-requests 10000 manage:app