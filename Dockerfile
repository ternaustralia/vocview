FROM python:3-alpine

RUN apk add --no-cache git

WORKDIR /app

RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir --upgrade setuptools

COPY ./controller /app/controller
COPY ./local_vocabs /app/local_vocabs
COPY ./skos /app/skos
COPY ./static /app/static
COPY ./templates /app/templates

COPY app.py /app
COPY config.py /app
COPY helper.py /app
COPY requirements.txt /app
COPY triplestore.py /app
COPY vocabs.yaml /app

COPY CHANGELOG.md /app

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

RUN chown -R 1000:1000 /app
USER 1000

CMD gunicorn --workers=1 --threads=2 --forwarded-allow-ips=* --bind=0.0.0.0:8000 --limit-request-line=8190 --log-level=info app:application