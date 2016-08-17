from django import forms
from django.core.exceptions import ValidationError

from .models import Season


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
