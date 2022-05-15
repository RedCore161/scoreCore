#!/bin/bash

if [ "$(id -u)" -ne "0" ]
  then echo "Please run as root"
  exit
fi

printf "Create Backup"
python3 manage.py dbbackup

printf "Rebuild Docker"
docker-compose down
docker-compose up -d --build

printf "Wait..."
sleep 30

printf "Restore Backup"
python3 manage.py dbrestore --noinput
