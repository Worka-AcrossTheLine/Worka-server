FROM python:3.7

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get -y install libpq-dev

WORKDIR /app
ADD . /app

RUN pip3 install -r requirements.txt


