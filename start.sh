#!/bin/sh
set -eu
export APP_ENV=production
python -m flask --app run db upgrade
exec gunicorn --config gunicorn.conf.py run:app
