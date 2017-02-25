from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import generic
from django.views.generic.base import ContextMixin

from escoresheet.utils.mixins import AccountAndSportRegistrationCompleteMixin


class CreateCoachesView(LoginRequiredMixin, ContextMixin, AccountAndSportRegistrationCompleteMixin, generic.View):
    template_name = 'coaches/coaches_create.html'

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(self.request, self.template_name, context)
