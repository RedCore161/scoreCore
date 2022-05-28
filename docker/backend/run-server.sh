#!/bin/bash

printf "\n\033[0;36m [INFO] Scoring-Backend will be started! \033[0m\n"

if [ -z "${1}" ]; then
  printf "\n\033[0;31m [EXIT] No Backend-Port given... \033[0m\n"
  exit 1
fi

rm -rf server/__pycache__/
rm -rf scoring/__pycache__/

printf "\n\033[0;36m ### Running Django-Scripts \033[0m\n"
python manage.py makemigrations
python manage.py migrate
python manage.py createadmin
python manage.py collectstatic --noinput

printf "\n\033[0;36m ### Starting Webserver \033[0m\n"
daphne -b 0.0.0.0 -p "${1}" server.asgi:application
