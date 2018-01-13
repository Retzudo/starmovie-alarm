from datetime import datetime

import pytz
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from core import models
from core.models import UserSettings


@receiver(post_save, sender=get_user_model())
def user_saved(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.create(user=instance)


@receiver(post_save, sender=models.ShowingDate)
def show_date_saved(sender, instance, created, **kwargs):
    now = datetime.now(tz=pytz.timezone(settings.TIME_ZONE))
    if created and instance.date >= now:
        # Notify users
        pass
