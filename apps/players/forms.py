from django import forms

from escoresheet.utils import set_fields_disabled, TeamModelChoiceField
from teams.models import Team
from . import models


class PlayerForm(forms.ModelForm):
    """
    Base form class for all player forms.
    """

    def __init__(self, *args, **kwargs):
        """
        Accepts the following kwargs

        :sport: The sport to filter teams by
        :read_only_fields: List of fields that should be disabled in an HTML form. Note that using this will make
            django think the form 'has_changed' when it really hasn't.
        """
        sport = kwargs.pop('sport', None)
        read_only_fields = kwargs.pop('read_only_fields', None)
        super(PlayerForm, self).__init__(*args, **kwargs)
        if sport is not None:
            self.fields['team'].queryset = Team.objects.filter(division__league__sport=sport).select_related('division')
        if read_only_fields is not None:
            set_fields_disabled(read_only_fields, self.fields)


class HockeyPlayerForm(PlayerForm):
    prefix = 'hockeyplayer'

    jersey_number = forms.IntegerField(min_value=models.HockeyPlayer.MIN_JERSEY_NUMBER,
                                       max_value=models.HockeyPlayer.MAX_JERSEY_NUMBER)

    team = TeamModelChoiceField(queryset=Team.objects.all().select_related('division'))

    class Meta:
        model = models.HockeyPlayer
        fields = ['team', 'jersey_number', 'position', 'handedness']


class BaseballPlayerForm(PlayerForm):
    prefix = 'baseballplayer'

    jersey_number = forms.IntegerField(min_value=models.BaseballPlayer.MIN_JERSEY_NUMBER,
                                       max_value=models.BaseballPlayer.MAX_JERSEY_NUMBER)

    team = TeamModelChoiceField(queryset=Team.objects.all().select_related('division'))

    class Meta:
        model = models.BaseballPlayer
        fields = ['team', 'jersey_number', 'position', 'catches', 'bats']


class BasketballPlayerForm(PlayerForm):
    prefix = 'basketballplayer'

    jersey_number = forms.IntegerField(min_value=models.BasketballPlayer.MIN_JERSEY_NUMBER,
                                       max_value=models.BasketballPlayer.MAX_JERSEY_NUMBER)

    team = TeamModelChoiceField(queryset=Team.objects.all().select_related('division'))

    class Meta:
        model = models.BasketballPlayer
        fields = ['team', 'jersey_number', 'position', 'shoots']
