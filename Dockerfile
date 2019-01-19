FROM python:3.6.8-alpine3.8

RUN mkdir -p /var/scripts/src && mkdir /var/scripts/db

COPY Pipfile /var/scripts
COPY Pipfile.lock /var/scripts

COPY src /var/scripts/src/

RUN apk --update add sqlite \
  && pip install pipenv \
  && rm -rf /var/cache/apk/*

WORKDIR /var/scripts
RUN pipenv install

CMD [ "pipenv", "run", "start" ]
