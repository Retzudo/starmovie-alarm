FROM python

COPY ./starmoviealert /starmoviealert

WORKDIR /starmoviealert

RUN pip install --no-cache-dir pipenv && pipenv install

CMD "pipenv run gunicorn starmoviealert.wsgi"