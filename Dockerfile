FROM python:3.9-buster

WORKDIR /src

COPY app/requirements.txt /src
RUN pip install -r /src/requirements.txt
COPY . /src

