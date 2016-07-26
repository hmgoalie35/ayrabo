from django import forms
from .models import HockeyPlayer


class HockeyPlayerForm(forms.ModelForm):
    prefix = 'hockeyplayer'

    jersey_number = forms.IntegerField(min_value=HockeyPlayer.MIN_JERSEY_NUMBER, max_value=HockeyPlayer.MAX_JERSEY_NUMBER)

    class Meta:
        model = HockeyPlayer
        exclude = ['user', 'sport']
