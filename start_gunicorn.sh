#!/bin/bash
/usr/bin/gunicorn --config gunicorn.conf  --daemon --reload  manage:app