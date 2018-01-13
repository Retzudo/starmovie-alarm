from datetime import datetime

import pytz
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Starmovie, Movie

BASE_URL = 'https://www.starmovie.at/star-movie-{location}'


class Command(BaseCommand):
    help = 'Retrieves movies for all available Starmovie locations'

    @staticmethod
    def _clean_movie_title(title: str) -> str:
        if title.startswith('OV:'):
            title = title[len('OV:'):]

        if title.lower().endswith('(englisch)'):
            title = title[:-len('(englisch)')]

        return title.strip()

    def fetch_movies(self, starmovie: Starmovie):
        url = BASE_URL.format(location=starmovie.location.lower())
        self.stdout.write('URL: {}'.format(url))
        html = requests.get(url).content
        soup = BeautifulSoup(html, 'html.parser')

        for movie_card in soup.find_all(class_='movie-card'):
            if 'hidden' in movie_card['class']:
                continue

            title = movie_card.find(class_='movie-card__header').string
            id = int(movie_card.find(class_='movie-card__rating')['data-movie-id'])
            try:
                movie = Movie.objects.get(pk=id)
                self.stdout.write('Movie "{}" already exists. Adding to "{}"'.format(title, starmovie.location))
            except Movie.DoesNotExist:
                self.stdout.write('Created movie "{}"'.format(self._clean_movie_title(title)))
                movie = Movie.objects.create(
                    pk=id,
                    title=self._clean_movie_title(title),
                    is_ov=title.lower().startswith('ov:'),
                )

            for time in movie_card.find_all(class_='movie-card__time'):
                timestamp = time['data-program-time']
                datetime_ = datetime.fromtimestamp(int(timestamp), tz=pytz.timezone(settings.TIME_ZONE))

                movie.showing_dates.create(date=datetime_, location=starmovie)

    def handle(self, *args, **options):
        for starmovie in Starmovie.objects.all():
            self.stdout.write('Fetching from location "{}"'.format(starmovie.location))
            self.fetch_movies(starmovie)
            self.stdout.write('################################\n\n')
