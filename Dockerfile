FROM python:3.9-alpine

RUN apk update && apk add build-base libffi-dev python3-dev

COPY . /unsafe_webpage

WORKDIR /unsafe_webpage

RUN mkdir /etc/app \
    && cp config.json /etc/app/config.json

RUN pip install -r requirements.txt
RUN pip install gunicorn==20.1.0

ENTRYPOINT ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
