from django import forms

from . import models


class HockeyPlayerForm(forms.ModelForm):
    prefix = 'hockeyplayer'

    jersey_number = forms.IntegerField(min_value=models.HockeyPlayer.MIN_JERSEY_NUMBER,
                                       max_value=models.HockeyPlayer.MAX_JERSEY_NUMBER)

    class Meta:
        model = models.HockeyPlayer
        exclude = ['user', 'sport']


class BaseballPlayerForm(forms.ModelForm):
    prefix = 'baseballplayer'

    jersey_number = forms.IntegerField(min_value=models.BaseballPlayer.MIN_JERSEY_NUMBER,
                                       max_value=models.BaseballPlayer.MAX_JERSEY_NUMBER)

    class Meta:
        model = models.BaseballPlayer
        exclude = ['user', 'sport']


class BasketballPlayerForm(forms.ModelForm):
    prefix = 'basketballplayer'

    jersey_number = forms.IntegerField(min_value=models.BasketballPlayer.MIN_JERSEY_NUMBER,
                                       max_value=models.BasketballPlayer.MAX_JERSEY_NUMBER)

    class Meta:
        model = models.BasketballPlayer
        exclude = ['user', 'sport']
