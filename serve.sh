#!/bin/sh

cd adm_portal && \
python manage.py migrate && \
gunicorn --bind 0.0.0.0:8000 --access-logfile - adm_portal.wsgi:application
