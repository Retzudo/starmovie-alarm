from datetime import datetime

import pytz
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import UpdateView, FormView

from core.models import Starmovie, Movie
from frontend import forms
from frontend.forms import UserCreationForm


def index(request):
    return render(request, 'frontend/index.html', context={
        'starmovies': Starmovie.objects.all().order_by('location')
    })


def show_movies(request, location):
    get_object_or_404(Starmovie, location=location)
    show_ov_only = request.user.is_authenticated and request.user.settings.only_show_ov and not request.GET.get('showall')

    all_movies = Movie.objects.filter(
        showing_dates__date__gte=datetime.now(pytz.timezone(settings.TIME_ZONE)),
        showing_dates__location__location__iexact=location,
    ).distinct().order_by('-is_ov', 'title')
    ov_movies = all_movies.filter(is_ov=True)

    if show_ov_only:
        movies = ov_movies
    else:
        movies = all_movies

    return render(request, 'frontend/starmovie.html', context={
        'movies': movies,
        'location': location,
        'all_movies': all_movies.count(),
        'ov_movies': ov_movies.count(),
        'show_ov_only': show_ov_only,
    })


def movie_details(request, location=None, movie_id=None):
    movie = get_object_or_404(Movie, pk=movie_id)
    if location:
        starmovie = get_object_or_404(Starmovie, location=location)
    else:
        starmovie = None

    return render(request, 'frontend/movie.html', context={
        'movie': movie,
        'starmovie': starmovie
    })


class ProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'frontend/profile.html'
    form_class = forms.ProfileForm
    success_url = '/accounts/profile'
    success_message = 'Settings saved!'

    def get_object(self, queryset=None):
        return self.request.user


class SettingsView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'frontend/settings.html'
    form_class = forms.SettingsForm
    success_url = '/accounts/settings'
    success_message = 'Settings saved!'

    def get_object(self, queryset=None):
        return self.request.user.settings


class RegisterView(FormView):
    template_name = 'frontend/register.html'
    form_class = UserCreationForm
    success_url = '/accounts/settings'

    def form_valid(self, form):
        form.save()
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
        login(self.request, user)
        return super().form_valid(form)
