from datetime import datetime

import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mass_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from core import models
from core.models import UserSettings


@receiver(post_save, sender=get_user_model())
def user_saved(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.create(user=instance)


@receiver(post_save, sender=models.ShowingDate)
def show_date_saved(sender, instance: models.ShowingDate, created, **kwargs):
    now = datetime.now(tz=pytz.timezone(settings.TIME_ZONE))
    if created and instance.date >= now:
        users = get_user_model().objects.filter(
            settings__favourite_location=instance.location,
            settings__receive_alert_emails=True,
            email__isnull=False,
        )
        addresses = [user.email for user in users]
        print('Sending to {} users with {} mail addresses'.format(len(users), len(addresses)))
        message = """Hello!
        
Starmovie {location} is showing a new movie in English!

Title: {movie}
Date: {date}""".format(
            location=instance.location.location,
            movie=instance.movie.title,
            date=instance,
        )

        if addresses:
            send_mass_mail(((
                'New OV Movies!',
                message,
                'noreply@starmovie.retzudo.com',
                addresses,
            ),))
