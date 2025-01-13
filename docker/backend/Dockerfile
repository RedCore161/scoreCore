FROM python:3.13-alpine AS python

RUN addgroup -S sudo && adduser -S -G sudo -h /home/scoring -g root -u 1312 scoring

ARG CONTROL_BACKEND_PORT
ARG DB_HOST
ARG DB_PORT
ARG MEDIA_VOLUME

ENV PROJECT_ROOT /usr/src/app
ENV VENV_ROOT /opt/venv
ENV PATH="$VENV_ROOT/bin:$PATH"
ENV DOMAIN="${DB_HOST}:${DB_PORT}"

WORKDIR ${PROJECT_ROOT}

RUN apk update && apk add --no-cache  \
                      ffmpeg \
                      nano \
                      iputils-ping \
                      lsb-release \
                      gnupg \
                      wget \
                      curl \
                      ca-certificates

RUN apk update && apk add git \
                      dcron \
                      rsync \
                      iputils-ping \
                      libpq-dev \
                      gcc

RUN apk add python3-dev musl-dev linux-headers make automake g++ bash

RUN wget https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -O wait-for-it.sh
RUN chmod +x wait-for-it.sh

VOLUME ${MEDIA_VOLUME}

COPY ./manage.py ./manage.py
COPY ./requirements.txt ./requirements.txt
COPY ./docker/backend/django.env ./django.env

RUN python3 -m venv $VENV_ROOT
RUN python3 -m ensurepip --upgrade
RUN pip install -U setuptools pip wheel

RUN . $VENV_ROOT/bin/activate

COPY ./docker/backend/ .
COPY ./scoring ./scoring
COPY ./server ./server

#Temp hotfix see https://github.com/pypa/setuptools/issues/4519
RUN pip install -U certifi wheel setuptools pip
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

RUN sed -i -e 's/\r$//' ./*.sh
RUN chmod +x ./*.sh

RUN [ ! -z "$CONTROL_BACKEND_PORT" ]
RUN [ ! -z "$DB_HOST" ]
RUN [ ! -z "$DB_PORT" ]

RUN echo "0 5 * * * /usr/src/app/scripts/createBackup.sh" >> /tmp/backUpJob
RUN crontab /tmp/backUpJob

RUN sed -i -e 's/\r$//' ./scripts/*.sh
RUN chmod +x ./scripts/*.sh

CMD ./wait-for-it.sh $DOMAIN -- ./run-server.sh "${CONTROL_BACKEND_PORT}"
