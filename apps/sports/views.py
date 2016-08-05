from django.views import generic
from .models import SportRegistration
from django.contrib.auth.mixins import LoginRequiredMixin


class CreateSportRegistrationView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'sports/sport_registration_create.html'
