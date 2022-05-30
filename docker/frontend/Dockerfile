ARG BACKEND_PORT
ARG HARD_IP

FROM node:18.2.0 as node

ARG BACKEND_PORT
ARG HARD_IP

WORKDIR /home/scoring/scoring-frontend
ENV PATH /home/scoring/scoring-frontend/node_modules/.bin:$PATH

COPY ./frontend .
COPY ./docker/frontend/.env.production .

RUN sed -i -r "s/BASE-URL-TEMPLATE/${HARD_IP}/g" ./.env.production
RUN sed -i -r "s/URL-TEMPLATE-WITH-PORT/${HARD_IP}:${BACKEND_PORT}/g" ./.env.production

RUN npm install
RUN npm run build

#CMD ["tail", "-f", "/dev/null"]
FROM nginx:stable-alpine
RUN adduser -S -D -h /home/scoring scoring

RUN rm /etc/nginx/conf.d/default.conf
COPY --from=node /home/scoring/scoring-frontend/build /usr/share/nginx/html
COPY ./docker/frontend/default.conf /etc/nginx/conf.d/default.conf
WORKDIR /usr/share/nginx/html

EXPOSE 80
