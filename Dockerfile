FROM python

RUN pip install pipenv

COPY . /starmoviealert
RUN cd /starmoviealert && pipenv install --system
RUN cd /starmoviealert/starmoviealert && python manage.py collectstatic --no-input

WORKDIR /starmoviealert/starmoviealert
CMD ["gunicorn", "--bind", "0.0.0.0:8020", "starmoviealert.wsgi"]