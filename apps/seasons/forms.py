from django import forms
from django.core.exceptions import ValidationError

from .models import Season


class SeasonAdminForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ['league', 'start_date', 'end_date', 'teams']

    def clean(self):
        league = self.cleaned_data.get('league', None)
        teams = self.cleaned_data.get('teams', None)
        errors = {'teams': []}
        if league and teams:
            for team in teams:
                if team.league_id != league.id:
                    errors['teams'].append(
                        'The team specified ({team_name}) does not belong to {league}'.format(
                            team_name=team.name, league=league.full_name))

            if errors['teams']:
                raise ValidationError(errors)
