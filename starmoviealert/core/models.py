from django.contrib.auth import get_user_model
from django.db import models


LOCATIONS = (
    ('Regau', 'Regau'),
    ('Liezen', 'Liezen'),
    ('Peuerbach', 'Peuerbach'),
    ('Ried', 'Ried'),
    ('Steyr', 'Steyr'),
    ('Wels', 'Wels')
)


class Starmovie(models.Model):
    location = models.CharField(max_length=15, choices=LOCATIONS, unique=True)

    def __str__(self):
        return 'Starmovie ' + self.location


class Movie(models.Model):
    locations = models.ManyToManyField(Starmovie, related_name='movies')
    movie_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    is_ov = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class ShowingDate(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showing_dates')
    date = models.DateTimeField()

    def __str__(self):
        return str(self.date)


class UserSettings(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='settings')
    favourite_location = models.ForeignKey(Starmovie, null=True, on_delete=models.SET_NULL, related_name='favourited_by_settings')
    receive_alert_emails = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'User settings'

    def __str__(self):
        return self.user.username