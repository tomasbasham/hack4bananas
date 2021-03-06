FROM python:3.7.5-buster
WORKDIR /usr/src/app

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
