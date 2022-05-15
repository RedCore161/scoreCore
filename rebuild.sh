#!/bin/bash

if [ "$(id -u)" -ne "0" ]
  then echo "Please run as root"
  exit
fi

printf "Create Backup"
docker exec -t scoring-backend python manage.py dbbackup

printf "Rebuild Docker"
docker-compose down
docker-compose up -d --build

printf "Wait..."
sleep 30

printf "Restore Backup"
docker exec -t scoring-backend python manage.py dbrestore --noinput
