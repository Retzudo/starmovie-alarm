from django import forms
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm as ContribUserCreationForm
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from core import models


class SettingsForm(ModelForm):
    class Meta:
        model = models.UserSettings
        exclude = ['user']


class UserCreationForm(ContribUserCreationForm):
    email = forms.EmailField(label=_('E-Mail'))

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user
