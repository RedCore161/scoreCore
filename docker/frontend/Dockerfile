ARG CONTROL_BACKEND_PORT
ARG CONTROL_BACKEND_URL
ARG CONTROL_FRONTEND_URL

FROM node:20 AS node

ARG CONTROL_BACKEND_PORT
ARG CONTROL_BACKEND_URL
ARG CONTROL_FRONTEND_URL

WORKDIR /home/scoring/scoring-frontend
ENV PATH /home/scoring/scoring-frontend/node_modules/.bin:$PATH

COPY ./frontend .
RUN npm install

COPY ./docker/frontend/.env.production .

RUN sed -i -r "s/BASE-FRONT-TEMPLATE/${CONTROL_FRONTEND_URL}/g" ./.env.production
RUN sed -i -r "s/BASE-BACK-TEMPLATE/${CONTROL_BACKEND_URL}/g" ./.env.production
RUN sed -i -r "s/URL-TEMPLATE-WITH-PORT/${CONTROL_BACKEND_URL}:${CONTROL_BACKEND_PORT}/g" ./.env.production

RUN npm run build

FROM nginx:1.27.3
RUN adduser -S -D -h /home/scoring scoring

RUN rm /etc/nginx/conf.d/default.conf
COPY --from=node /home/scoring/scoring-frontend/dist /usr/share/nginx/html
COPY ./docker/frontend/default.conf /etc/nginx/conf.d/default.conf
WORKDIR /usr/share/nginx/html

EXPOSE 80
