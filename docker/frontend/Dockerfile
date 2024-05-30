ARG CONTROL_BACKEND_PORT
ARG CONTROL_BACKEND_URL

FROM node:18 as node

ARG CONTROL_BACKEND_PORT
ARG CONTROL_BACKEND_URL

WORKDIR /home/scoring/scoring-frontend
ENV PATH /home/scoring/scoring-frontend/node_modules/.bin:$PATH

COPY ./frontend .
COPY ./docker/frontend/.env.production .

RUN sed -i -r "s/BASE-URL-TEMPLATE/${CONTROL_BACKEND_URL}/g" ./.env.production
RUN sed -i -r "s/URL-TEMPLATE-WITH-PORT/${CONTROL_BACKEND_URL}:${CONTROL_BACKEND_PORT}/g" ./.env.production

RUN npm install
RUN npm run build


FROM nginx:stable-alpine
RUN adduser -S -D -h /home/scoring scoring

RUN rm /etc/nginx/conf.d/default.conf
COPY --from=node /home/scoring/scoring-frontend/build /usr/share/nginx/html
COPY --from=node /home/scoring/scoring-frontend/.env.production /tmp/.env.production
COPY ./docker/frontend/default.conf /etc/nginx/conf.d/default.conf
WORKDIR /usr/share/nginx/html

EXPOSE 80
