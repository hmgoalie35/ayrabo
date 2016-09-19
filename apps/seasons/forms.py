from django import forms
from django.contrib.admin import widgets
from django.core.exceptions import ValidationError

from escoresheet.fields import SeasonModelChoiceField, TeamModelChoiceField
from players.models import HockeyPlayer
from teams.models import Team
from .models import Season, HockeySeasonRoster


class SeasonAdminForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ['division', 'start_date', 'end_date', 'teams']

    def clean(self):
        division = self.cleaned_data.get('division', None)
        teams = self.cleaned_data.get('teams', None)
        errors = {'teams': []}
        if division and teams:
            for team in teams:
                if team.division_id != division.id:
                    errors['teams'].append(
                            'The team specified ({team_name}) does not belong to {division} - {league}'.format(
                                    team_name=team.name, division=division.name, league=division.league.full_name))

            if errors['teams']:
                raise ValidationError(errors)


class HockeySeasonRosterAdminForm(forms.ModelForm):
    """
    Custom admin form that optimizes db access for certain model fields.
    """

    sport_name = 'Hockey'

    season = SeasonModelChoiceField(
            queryset=Season.objects.filter(division__league__sport__name__icontains=sport_name).select_related(
                    'division'))
    team = TeamModelChoiceField(
            queryset=Team.objects.filter(division__league__sport__name__icontains=sport_name).select_related(
                    'division'))

    players = forms.ModelMultipleChoiceField(queryset=HockeyPlayer.objects.all().select_related('user'),
                                             widget=widgets.FilteredSelectMultiple(verbose_name='Players',
                                                                                   is_stacked=False))

    class Meta:
        model = HockeySeasonRoster
        fields = '__all__'
