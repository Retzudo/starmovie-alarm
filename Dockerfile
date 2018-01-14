FROM python

COPY . /starmoviealert
RUN pip install -r /starmovie/requirements.txt
RUN cd /starmoviealert/starmoviealert && python manage.py collectstatic --no-input

WORKDIR /starmoviealert/starmoviealert
CMD ["gunicorn", "--bind", "0.0.0.0:8020", "starmoviealert.wsgi"]