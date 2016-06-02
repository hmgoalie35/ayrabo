from django.shortcuts import render
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Sport
from django.core.urlresolvers import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin


class CreateSportView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Sport
    template_name = 'sports/create.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('home')

    def get_success_message(self, cleaned_data):
        return '{sport} successfully created'.format(sport=self.object.name)

    # def form_invalid(self, form):
    #     # override error message
    #     pass
    #
    # def form_valid(self, form):
    #     # before calling super, convert name to title case
    #     pass
