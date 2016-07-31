from django import forms

from .models import HockeyPlayer, BaseballPlayer


class HockeyPlayerForm(forms.ModelForm):
    prefix = 'hockeyplayer'

    jersey_number = forms.IntegerField(min_value=HockeyPlayer.MIN_JERSEY_NUMBER,
                                       max_value=HockeyPlayer.MAX_JERSEY_NUMBER)

    class Meta:
        model = HockeyPlayer
        exclude = ['user', 'sport']


class BaseballPlayerForm(forms.ModelForm):
    prefix = 'baseballplayer'

    jersey_number = forms.IntegerField(min_value=BaseballPlayer.MIN_JERSEY_NUMBER,
                                       max_value=BaseballPlayer.MAX_JERSEY_NUMBER)

    class Meta:
        model = BaseballPlayer
        exclude = ['user', 'sport']
