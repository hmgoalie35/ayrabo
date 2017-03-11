from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import generic
from django.views.generic.base import ContextMixin

from escoresheet.utils.mixins import AccountAndSportRegistrationCompleteMixin


class CreateRefereesView(LoginRequiredMixin, ContextMixin, AccountAndSportRegistrationCompleteMixin, generic.View):
    template_name = 'referees/referees_create.html'

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(self.request, self.template_name, context)
