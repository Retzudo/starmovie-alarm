from datetime import datetime

import pytz
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import UpdateView

from core.models import Starmovie, Movie
from frontend import forms


def index(request):
    return render(request, 'frontend/index.html', context={
        'starmovies': Starmovie.objects.all()
    })


def show_movies(request, location):
    get_object_or_404(Starmovie, location=location)

    movies = Movie.objects.filter(
        showing_dates__date__gte=datetime.now(pytz.timezone(settings.TIME_ZONE)),
        showing_dates__location__location__iex=location,
    ).distinct().order_by('-is_ov', 'title')

    if request.user.is_authenticated and request.user.settings.only_show_ov:
        movies = movies.filter(is_ov=True)

    return render(request, 'frontend/starmovie.html', context={
        'movies': movies
    })


class SettingsView(LoginRequiredMixin, UpdateView):
    template_name = 'frontend/settings.html'
    form_class = forms.SettingsForm
    success_url = '/accounts/settings'

    def get_object(self, queryset=None):
        return self.request.user.settings
