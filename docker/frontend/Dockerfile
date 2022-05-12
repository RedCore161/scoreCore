ARG BASE_URL
ARG BACKEND_PORT

FROM node:16.3.0 as node

ARG BASE_URL
ARG BACKEND_PORT

WORKDIR /home/scoring/scoring-frontend
ENV PATH /home/scoring/scoring-frontend/node_modules/.bin:$PATH

COPY ./docker/frontend/.env.production .
COPY ./frontend .

RUN sed -i -r "s/URL-TEMPLATE/${BASE_URL}:${BACKEND_PORT}/g" ./.env.production

RUN npm install
RUN npm run build


FROM nginx:stable-alpine
RUN adduser -S -D -h /home/testing testing

RUN rm /etc/nginx/conf.d/default.conf
COPY --from=node /home/scoring/scoring-frontend/build /usr/share/nginx/html
COPY ./docker/frontend/default.conf /etc/nginx/conf.d/default.conf
WORKDIR /usr/share/nginx/html

EXPOSE 80
