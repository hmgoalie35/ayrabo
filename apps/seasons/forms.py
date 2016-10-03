# from django import forms
# from django.contrib.admin import widgets
# from django.core.exceptions import ValidationError
#
# from escoresheet.fields import SeasonModelChoiceField, TeamModelChoiceField
# from players.models import HockeyPlayer
# from teams.models import Team
# from .models import Season, HockeySeasonRoster
#
#
# class SeasonAdminForm(forms.ModelForm):
#     class Meta:
#         model = Season
#         fields = ['league', 'start_date', 'end_date', 'teams']
#
#     def clean(self):
#         league = self.cleaned_data.get('league', None)
#         teams = self.cleaned_data.get('teams', None)
#         errors = {'teams': []}
#         if league and teams:
#             for team in teams:
#                 if team.league_id != league.id:
#                     errors['teams'].append(
#                             'The team specified ({team_name}) does not belong to {league}'.format(
#                                     team_name=team.name, league=league.full_name))
#
#             if errors['teams']:
#                 raise ValidationError(errors)
#
#
# class HockeySeasonRosterAdminForm(forms.ModelForm):
#     """
#     Custom admin form that optimizes db access for certain model fields.
#     """
#
#     sport_name = 'Hockey'
#
#     season = SeasonModelChoiceField(
#             queryset=Season.objects.filter(league__sport__name__icontains=sport_name).select_related(
#                     'league'))
#     team = TeamModelChoiceField(
#             queryset=Team.objects.filter(league__sport__name__icontains=sport_name).select_related(
#                     'league'))
#
#     players = forms.ModelMultipleChoiceField(queryset=HockeyPlayer.objects.all().select_related('user'),
#                                              widget=widgets.FilteredSelectMultiple(verbose_name='Players',
#                                                                                    is_stacked=False))
#
#     class Meta:
#         model = HockeySeasonRoster
#         fields = '__all__'
