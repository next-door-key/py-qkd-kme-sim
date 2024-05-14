# syntax=docker/dockerfile:1

FROM python:3.10-alpine3.18

ENV PYTHONUNBUFFERED=1

COPY . /opt/next-door-key-simulator
WORKDIR /opt/next-door-key-simulator

RUN apk add -U --no-cache bash curl

RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

RUN pip3 install --no-cache -r requirements.txt

CMD fastapi run app/main.py