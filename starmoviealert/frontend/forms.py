from django.forms import ModelForm

from core import models


class SettingsForm(ModelForm):
    class Meta:
        model = models.UserSettings
        exclude = ['user']
