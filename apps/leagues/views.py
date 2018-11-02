from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from leagues.models import League


class LeagueDetailView(LoginRequiredMixin, DetailView):
    template_name = 'leagues/league_detail.html'
    context_object_name = 'league'
    queryset = League.objects.select_related('sport')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
