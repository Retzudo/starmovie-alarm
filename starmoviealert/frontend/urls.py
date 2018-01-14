from django.urls import path

from frontend import views

urlpatterns = [
    path('', views.index, name='index'),
    path('starmovie/<str:location>', views.show_movies, name='show_movies'),
    path('accounts/settings', views.SettingsView.as_view(), name='settings'),
    path('accounts/register', views.RegisterView.as_view(), name='register'),
    path('accounts/profile/', views.ProfileView.as_view(), name='profile'),
]