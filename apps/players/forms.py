from django import forms

from teams.models import Team
from . import models


class HockeyPlayerForm(forms.ModelForm):
    prefix = 'hockeyplayer'

    def __init__(self, *args, **kwargs):
        sport = kwargs.pop('sport', None)
        super(HockeyPlayerForm, self).__init__(*args, **kwargs)
        if sport is not None:
            self.fields['team'].queryset = Team.objects.filter(division__league__sport=sport)

    jersey_number = forms.IntegerField(min_value=models.HockeyPlayer.MIN_JERSEY_NUMBER,
                                       max_value=models.HockeyPlayer.MAX_JERSEY_NUMBER)

    class Meta:
        model = models.HockeyPlayer
        exclude = ['user', 'sport']


class BaseballPlayerForm(forms.ModelForm):
    prefix = 'baseballplayer'

    def __init__(self, *args, **kwargs):
        sport = kwargs.pop('sport', None)
        super(BaseballPlayerForm, self).__init__(*args, **kwargs)
        if sport is not None:
            self.fields['team'].queryset = Team.objects.filter(division__league__sport=sport)

    jersey_number = forms.IntegerField(min_value=models.BaseballPlayer.MIN_JERSEY_NUMBER,
                                       max_value=models.BaseballPlayer.MAX_JERSEY_NUMBER)

    class Meta:
        model = models.BaseballPlayer
        exclude = ['user', 'sport']


class BasketballPlayerForm(forms.ModelForm):
    prefix = 'basketballplayer'

    def __init__(self, *args, **kwargs):
        sport = kwargs.pop('sport', None)
        super(BasketballPlayerForm, self).__init__(*args, **kwargs)
        if sport is not None:
            self.fields['team'].queryset = Team.objects.filter(division__league__sport=sport)

    jersey_number = forms.IntegerField(min_value=models.BasketballPlayer.MIN_JERSEY_NUMBER,
                                       max_value=models.BasketballPlayer.MAX_JERSEY_NUMBER)

    class Meta:
        model = models.BasketballPlayer
        exclude = ['user', 'sport']
