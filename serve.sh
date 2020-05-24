#!/bin/sh

cd adm_portal && \
python manage.py migrate && \
gunicorn --workers=2 --threads=4 --worker-class=gthread --bind 0.0.0.0:8000 --access-logfile - adm_portal.wsgi:application
