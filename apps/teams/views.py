from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView

from ayrabo.utils.mixins import HandleSportNotConfiguredMixin
from common.views import CsvBulkUploadView
from divisions.models import Division
from games.utils import get_game_list_view_context
from organizations.models import Organization
from seasons.models import Season
from teams.utils import get_team_detail_view_context
from .models import Team


class BulkUploadTeamsView(CsvBulkUploadView):
    success_url = reverse_lazy('bulk_upload_teams')
    model = Team
    fields = ('name', 'website', 'division', 'organization')

    def get_division(self, value, row):
        divisions = Division.objects.filter(name=value)
        if divisions.exists():
            return divisions.first().id
        return value

    def get_organization(self, value, row):
        organizations = Organization.objects.filter(name=value)
        if organizations.exists():
            return organizations.first().id
        return value

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_cls'] = 'Team'
        context['url'] = reverse_lazy('admin:teams_team_changelist')
        return context


class AbstractTeamDetailView(LoginRequiredMixin, HandleSportNotConfiguredMixin, DetailView):
    context_object_name = 'team'
    pk_url_kwarg = 'team_pk'
    queryset = Team.objects.select_related('division__league__sport')

    def get_object(self, queryset=None):
        if hasattr(self, 'object'):
            return self.object
        self.object = super().get_object(queryset)
        self.division = self.object.division
        self.league = self.division.league
        self.sport = self.league.sport
        return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.get_object()
        context.update(get_team_detail_view_context(team))
        return context


class TeamDetailScheduleView(AbstractTeamDetailView):
    template_name = 'teams/team_detail_schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        team = self.get_object()
        current_season = Season.objects.get_current(league=self.league)
        game_list_context = get_game_list_view_context(user, self.sport, current_season, team=team)
        team_ids_managed_by_user = game_list_context.get('team_ids_managed_by_user')
        context.update({
            'can_create_game': team.id in team_ids_managed_by_user,
        })
        context.update(game_list_context)
        return context
