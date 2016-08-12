from django import forms

from escoresheet.utils import set_fields_disabled
from teams.models import Team
from . import models
from escoresheet.fields import TeamModelChoiceField


class HockeyPlayerForm(forms.ModelForm):
    prefix = 'hockeyplayer'

    def __init__(self, *args, **kwargs):
        """
        Override the constructor to allow for custom kwargs to be passed to this form.
        sport -- The sport to filter teams by
        read_only_fields -- A list of fields that should be disabled in an HTML form. Note that using this will make
        django think the form 'has_changed' when it really hasn't.
        """
        sport = kwargs.pop('sport', None)
        read_only_fields = kwargs.pop('read_only_fields', None)
        super(HockeyPlayerForm, self).__init__(*args, **kwargs)
        if sport is not None:
            self.fields['team'].queryset = Team.objects.filter(division__league__sport=sport).select_related('division')
        if read_only_fields is not None:
            set_fields_disabled(read_only_fields, self.fields)

    jersey_number = forms.IntegerField(min_value=models.HockeyPlayer.MIN_JERSEY_NUMBER,
                                       max_value=models.HockeyPlayer.MAX_JERSEY_NUMBER)

    team = TeamModelChoiceField(queryset=Team.objects.all().select_related('division'))

    class Meta:
        model = models.HockeyPlayer
        exclude = ['user', 'sport']


class BaseballPlayerForm(forms.ModelForm):
    prefix = 'baseballplayer'

    def __init__(self, *args, **kwargs):
        """
        Override the constructor to allow for custom kwargs to be passed to this form.
        sport -- The sport to filter teams by
        read_only_fields -- A list of fields that should be disabled in an HTML form. Note that using this will make
        django think the form 'has_changed' when it really hasn't.
        """
        sport = kwargs.pop('sport', None)
        read_only_fields = kwargs.pop('read_only_fields', None)
        super(BaseballPlayerForm, self).__init__(*args, **kwargs)
        if sport is not None:
            self.fields['team'].queryset = Team.objects.filter(division__league__sport=sport).select_related('division')
        if read_only_fields is not None:
            set_fields_disabled(read_only_fields, self.fields)

    jersey_number = forms.IntegerField(min_value=models.BaseballPlayer.MIN_JERSEY_NUMBER,
                                       max_value=models.BaseballPlayer.MAX_JERSEY_NUMBER)

    team = TeamModelChoiceField(queryset=Team.objects.all().select_related('division'))

    class Meta:
        model = models.BaseballPlayer
        exclude = ['user', 'sport']


class BasketballPlayerForm(forms.ModelForm):
    prefix = 'basketballplayer'

    def __init__(self, *args, **kwargs):
        """
        Override the constructor to allow for custom kwargs to be passed to this form.
        sport -- The sport to filter teams by
        read_only_fields -- A list of fields that should be disabled in an HTML form. Note that using this will make
        django think the form 'has_changed' when it really hasn't.
        """
        sport = kwargs.pop('sport', None)
        read_only_fields = kwargs.pop('read_only_fields', None)
        super(BasketballPlayerForm, self).__init__(*args, **kwargs)
        if sport is not None:
            self.fields['team'].queryset = Team.objects.filter(division__league__sport=sport).select_related('division')
        if read_only_fields is not None:
            set_fields_disabled(read_only_fields, self.fields)

    jersey_number = forms.IntegerField(min_value=models.BasketballPlayer.MIN_JERSEY_NUMBER,
                                       max_value=models.BasketballPlayer.MAX_JERSEY_NUMBER)
    team = TeamModelChoiceField(queryset=Team.objects.all().select_related('division'))

    class Meta:
        model = models.BasketballPlayer
        exclude = ['user', 'sport']
