from datetime import datetime
from typing import List

import pytz
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.core.mail import send_mass_mail
from django.core.management.base import BaseCommand

from core.models import Starmovie, Movie, ShowingDate

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

    @staticmethod
    def _get_poster_url(movie_card) -> str:
        img = movie_card.find(class_='movie-card__image')
        srcset = img['data-srcset'].split()

        return srcset[srcset.index('2x') - 1].strip()

    def fetch_movies(self, starmovie: Starmovie) -> List[ShowingDate]:
        url = BASE_URL.format(location=starmovie.location.lower())
        self.stdout.write('URL: {}'.format(url))
        html = requests.get(url).content
        soup = BeautifulSoup(html, 'html.parser')
        dates_created = []

        for movie_card in soup.find_all(class_='movie-card'):
            if 'hidden' in movie_card['class']:
                continue

            title = movie_card.find(class_='movie-card__header').string
            id = int(movie_card.find(class_='movie-card__rating')['data-movie-id'])
            poster_url = self._get_poster_url(movie_card)
            if poster_url.startswith('/'):
                poster_url = 'https://www.starmovie.at' + poster_url

            try:
                movie = Movie.objects.get(pk=id)
                self.stdout.write('Movie "{}" already exists'.format(title))
            except Movie.DoesNotExist:
                self.stdout.write('Created movie "{}"'.format(self._clean_movie_title(title)))
                movie = Movie.objects.create(
                    pk=id,
                    title=self._clean_movie_title(title),
                    is_ov=title.lower().startswith('ov:'),
                    poster_url=poster_url,
                )

            details_url = movie_card.find(class_='movie-card__detail-link')['href']
            if details_url.startswith('/'):
                details_url = 'https://www.starmovie.at' + details_url

            for time in movie_card.find_all(class_='movie-card__time'):
                timestamp = time['data-program-time']
                datetime_ = datetime.fromtimestamp(int(timestamp), tz=pytz.timezone(settings.TIME_ZONE))

                try:
                    movie.showing_dates.get(date=datetime_, location=starmovie)
                except ShowingDate.DoesNotExist:
                    date = movie.showing_dates.create(date=datetime_, location=starmovie, details_url=details_url)
                    dates_created.append(date)
                    self.stdout.write('Showing date created in {} {}'.format(starmovie.location, datetime_))

        return dates_created

    def send_emails(self, dates_created: List[ShowingDate]):
        if not dates_created:
            return

        # messages_to_send = []

        for location in Starmovie.objects.all():
            # Get all users for this location who have an email address and want to receive alerts.
            users = get_user_model().objects.filter(
                settings__receive_alert_emails=True,
                settings__favourite_location=location,
                email__isnull=False,
            )
            # If there are no users, skip to the next location
            if len(users) < 1:
                continue

            # Filter created showing dates by this location and OV only.
            for_location = list(filter(lambda showing_date: showing_date.location == location and showing_date.movie.is_ov, dates_created))
            message = 'Hello!\n\r\n\rStarmovie {} has added new showing dates for movies in English!\n\r\n\r'.format(location.location)

            # If there are no showing dates left, skip to the next location.
            if not for_location:
                continue

            self.stdout.write('Sending notification for {} movie(s) to {} users with an e-mail address'.format(len(for_location), len(users)))

            # Add a line for every showing date.
            for date in for_location:
                message += 'Title: {}\n\rDate: {}\n\rURL: {}\n\r----------------------------\n\r'.format(date.movie.title, date.date, date.details_url)

            with mail.get_connection() as connection:
                for user in users:
                    mail.EmailMessage(
                        subject='New OV Movies!',
                        body=message,
                        from_email='Starmovie Alert <noreply@starmovie.retzudo.com>',
                        to=[user.email],
                        connection=connection,
                    ).send()

    def handle(self, *args, **options):
        dates_created = []
        for starmovie in Starmovie.objects.all():
            self.stdout.write('Fetching from location "{}"'.format(starmovie.location))
            dates_created += self.fetch_movies(starmovie)
            self.stdout.write('################################\n\n')

        self.send_emails(dates_created)
