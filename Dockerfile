FROM python:slim

ENV FILE_EXPORTER_PATH=None

EXPOSE 5000

WORKDIR /opt/app

VOLUME /opt/app/data

COPY requirements.txt .

RUN pip install -U pip && pip install -r requirements.txt && pip install gunicorn

COPY . .

CMD gunicorn -b 0.0.0.0:5000 wsgi:app
