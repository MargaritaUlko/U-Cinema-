import datetime
import json
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Hall, Movie, Session
from .models import User

class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'description', 'poster']



class MultiDateSessionForm(forms.Form):
    movie = forms.ModelChoiceField(queryset=Movie.objects.all(), label="Выберите фильм")  # Здесь изменена метка
    ticket_price = forms.DecimalField(max_digits=10, decimal_places=2, label="Цена билета")  # Здесь тоже изменена метка
    sessions = forms.CharField(widget=forms.HiddenInput(), required=False)
    hall = forms.ModelChoiceField(queryset=Hall.objects.all(), label="Выберите зал")  # Здесь изменена метка

    def clean(self):
        cleaned_data = super().clean()
        sessions_data = cleaned_data.get("sessions")

        if sessions_data:
            sessions_list = []
            for session_data in sessions_data.split(";"):
                date_time_str = session_data.strip()
                if date_time_str:
                    try:
                        date, time = date_time_str.split(" ")
                        sessions_list.append({"date": date, "time": time})
                    except ValueError:
                        raise forms.ValidationError("Некорректный формат даты и времени.")
            cleaned_data['sessions_list'] = sessions_list
        return cleaned_data

