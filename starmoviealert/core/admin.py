from django.contrib import admin

from core import models

admin.site.register(models.Movie)
admin.site.register(models.UserSettings)
admin.site.register(models.Starmovie)