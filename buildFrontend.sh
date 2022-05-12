#!/bin/bash

if ! [ "$(id -u)" = 0 ]; then
   echo "The script need to be run as root." >&2
   exit 1
fi

if [ $SUDO_USER ]; then
    real_user=$SUDO_USER
else
    real_user=$(whoami)
fi

cd /home/scoring/scoring/frontend/ || exit

sudo -u $real_user npm install
sudo -u $real_user npm run build
sudo -u $real_user cp build/ /var/www/scoring/html/

sudo systemctl restart gunicorn_scoring.service
