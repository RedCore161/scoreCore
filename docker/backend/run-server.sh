#!/bin/bash
function pprint() {
   printf "\n\033[0;36m${1}\033[0m\n"
}

pprint "[INFO] Scoring-Backend will be started!"

if [ -z "${1}" ]; then
  pprint "[EXIT] No Backend-Port given..."
  exit 1
fi

rm -rf server/__pycache__/
rm -rf scoring/__pycache__/

pprint "### Running Django-Scripts for ${DOMAIN}"
pprint "[1] collectstatic"
python manage.py collectstatic --noinput

pprint "[2] makemigrations"
python manage.py makemigrations

pprint "[3] migrate"
python manage.py migrate --noinput

pprint "[4] createadmin"
python manage.py createadmin

pprint "[5] clear_token"
python manage.py clear_token

if [ "$CELERY_ON_BOOT" = "1" ]; then
  pprint "[6] celery worker"
  celery -A scoring.celery worker --loglevel=info --logfile "${PROJECT_ROOT}/celery.log" -E -P eventlet --uid=1312 &
fi

pprint "### Starting Webserver"
daphne -b 0.0.0.0 -p "${1}" server.asgi:application
