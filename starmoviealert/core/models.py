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
    movie_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    is_ov = models.BooleanField(default=False)
    poster_url = models.URLField(null=True)

    def __str__(self):
        return self.title

    @property
    def locations(self):
        return Starmovie.objects.filter(
            pk__in=self.showing_dates.all().values_list('location', flat=True)
        )


class ShowingDate(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showing_dates')
    date = models.DateTimeField()
    location = models.ForeignKey(Starmovie, on_delete=models.CASCADE, related_name='showing_dates')
    details_url = models.URLField()

    def __str__(self):
        return str(self.date)


class UserSettings(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='settings')
    favourite_location = models.ForeignKey(Starmovie, null=True, on_delete=models.SET_NULL, related_name='favourited_by_settings')
    receive_alert_emails = models.BooleanField(default=True)
    only_show_ov = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'User settings'

    def __str__(self):
        return self.user.username