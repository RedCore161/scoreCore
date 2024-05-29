ARG CONTROL_BACKEND_PORT
ARG DB_HOST
ARG DB_PORT
ARG MEDIA_VOLUME

FROM solutiance/django-opencv:1.1.3
RUN useradd -rm -d /home/scoring -s /bin/sh -g root -G sudo -u 1001 scoring

ARG CONTROL_BACKEND_PORT
ARG DB_HOST
ARG DB_PORT
ARG MEDIA_VOLUME

ENV PROJECT_ROOT /usr/src/app
WORKDIR ${PROJECT_ROOT}

RUN wget https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -O wait-for-it.sh
RUN chmod +x wait-for-it.sh

VOLUME ${MEDIA_VOLUME}

COPY ./manage.py ./manage.py
COPY ./requirements.txt ./requirements.txt
COPY ./docker/backend/django.env ./django.env

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./docker/backend/ .
COPY ./scoring ./scoring
COPY ./server ./server

EXPOSE 6379
EXPOSE 5432
EXPOSE 80

RUN sed -i -e 's/\r$//' ./*.sh
RUN chmod +x ./*.sh

RUN [ ! -z "$CONTROL_BACKEND_PORT" ]
RUN [ ! -z "$DB_HOST" ]
RUN [ ! -z "$DB_PORT" ]

RUN apt update && \
    apt install -y nano iputils-ping cron postgresql-client

ENV DOMAIN="${DB_HOST}:${DB_PORT}"

RUN echo "0 5 * * * /usr/src/app/scripts/createBackup.sh" >> /tmp/backUpJob
RUN crontab /tmp/backUpJob

RUN sed -i -e 's/\r$//' ./scripts/*.sh
RUN chmod +x ./scripts/*.sh

#USER scoring # Fix later
CMD ./wait-for-it.sh $DOMAIN -- ./run-server.sh "${CONTROL_BACKEND_PORT}"
