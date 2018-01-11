from datetime import datetime

import pytz
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from core.models import Starmovie, Movie

BASE_URL = 'https://www.starmovie.at/star-movie-{location}'


def clean_movie_title(title: str) -> str:
    if title.startswith('OV:'):
        title = title[len('OV:'):]

    if title.lower().endswith('(englisch)'):
        title = title[:-len('(englisch)')]

    return title.strip()


def fetch_movies(starmovie: Starmovie):
    url = BASE_URL.format(location=starmovie.location.lower())
    html = requests.get(url).content
    soup = BeautifulSoup(html, 'html.parser')

    for movie_card in soup.find_all(class_='movie-card'):
        if 'hidden' in movie_card['class']:
            continue

        title = movie_card.find(class_='movie-card__header').string
        id = int(movie_card.find(class_='movie-card__rating')['data-movie-id'])
        try:
            movie = Movie.objects.get(pk=id)
        except Movie.DoesNotExist:
            movie = Movie.objects.create(
                starmovie=starmovie,
                pk=id,
                title=clean_movie_title(title),
                is_ov=title.lower().startswith('ov:')
            )

        for time in movie_card.find_all(class_='movie-card__time'):
            timestamp = time['data-program-time']
            datetime_ = datetime.fromtimestamp(int(timestamp), tz=pytz.timezone('Europe/Vienna'))

            movie.showing_dates.create(date=datetime_)


class Command(BaseCommand):
    help = 'Retrieves movies for all available Starmovie locations'

    def handle(self, *args, **options):
        for starmovie in Starmovie.objects.all():
            fetch_movies(starmovie)