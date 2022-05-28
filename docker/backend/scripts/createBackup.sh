#!/bin/bash

cd "${PROJECT_ROOT}" || exit

printf "[BACKUP] Create Backup"
python manage.py dbbackup

printf "[BACKUP] Notify Django"
python manage.py notify --created-backup=1
