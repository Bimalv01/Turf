# turff_App/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

class TurfOwnerRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class TurfOwnerLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class TurfForm(forms.ModelForm):
    class Meta:
        model = Turf
        fields = ['turffname', 'location', 'turf_type', 'phone_number', 'price']

class TurfSearchForm(forms.Form):
    location = forms.CharField(max_length=255, required=False)
    turf_type = forms.ChoiceField(
        choices=[('', 'Select Type'), ('5s', '5s'), ('7s', '7s'), ('11s', '11s')],
        required=False
    )
