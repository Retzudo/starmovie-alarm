from django.shortcuts import render

from core.models import Starmovie


def index(request):
    return render(request, 'frontend/index.html', context={
        'starmovies': Starmovie.objects.all()
    })


def show_movies(request, starmovie_location):
    pass