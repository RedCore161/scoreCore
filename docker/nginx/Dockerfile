FROM nginx:1.21.3

WORKDIR /etc/nginx/
COPY ./docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf

RUN useradd -rm -d /home/scoring -s /bin/sh -g root -G sudo -u 1312 scoring
#USER scoring
