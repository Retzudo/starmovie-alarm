from datetime import datetime

import pytz
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView

from core.models import Starmovie, Movie


def index(request):
    return render(request, 'frontend/index.html', context={
        'starmovies': Starmovie.objects.all()
    })


def show_movies(request, location):
    starmovie = get_object_or_404(Starmovie, location=location)

    movies = Movie.objects.filter(
        showing_dates__date__gte=datetime.now(pytz.timezone(settings.TIME_ZONE)),
        showing_dates__location__location__iexact=location,
    ).distinct()

    return render(request, 'frontend/starmovie.html', context={
        'movies': movies
    })


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'frontend/settings.html'
