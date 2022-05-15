ARG BACKEND_PORT
ARG DB_HOST
ARG DB_PORT

FROM solutiance/django-opencv:1.0.0
RUN useradd -rm -d /home/scoring -s /bin/sh -g root -G sudo -u 1001 scoring

ARG BACKEND_PORT
ARG DB_HOST
ARG DB_PORT

ENV PROJECT_ROOT /usr/src/app
WORKDIR ${PROJECT_ROOT}

RUN wget https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -O wait-for-it.sh
RUN chmod +x wait-for-it.sh

COPY ./docker/backend/ .
COPY ./scoring ./scoring
COPY ./server ./server

VOLUME ./media

COPY ./manage.py ./manage.py
COPY ./requirements.txt ./requirements.txt
COPY ./docker/backend/django.env ./django.env

RUN pip install -r requirements.txt

EXPOSE 6379
EXPOSE 5432
EXPOSE 80

RUN sed -i -e 's/\r$//' ./*.sh
RUN chmod +x ./*.sh

RUN [ ! -z "$BACKEND_PORT" ]
RUN [ ! -z "$DB_HOST" ]
RUN [ ! -z "$DB_PORT" ]

RUN apt update && \
    apt install -y nano iputils-ping cron postgresql-client

ENV DOMAIN="${DB_HOST}:${DB_PORT}"
ENV PORT=${BACKEND_PORT}

RUN echo "0 5 * * * python manage.py dbbackup" >> /tmp/backUpJob
RUN crontab /tmp/backUpJob

#USER scoring # Fix later
CMD ./wait-for-it.sh $DOMAIN -- ./run-server.sh "${PORT}"
