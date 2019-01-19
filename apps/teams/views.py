from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView

from common.views import CsvBulkUploadView
from divisions.models import Division
from organizations.models import Organization
from seasons.models import Season
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


class AbstractTeamDetailView(LoginRequiredMixin, DetailView):
    context_object_name = 'team'
    pk_url_kwarg = 'team_pk'
    queryset = Team.objects.select_related('division__league')

    def get_object(self, queryset=None):
        if hasattr(self, 'object'):
            return self.object
        self.object = super().get_object(queryset)
        return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.object
        context.update({
            'team_display_name': f'{team.name} - {team.division.name}',
            'past_seasons': Season.objects.get_past(league=team.division.league)
        })
        return context


class TeamDetailScheduleView(AbstractTeamDetailView):
    template_name = 'teams/team_detail_schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'active_tab': 'schedule'
        })
        return context
