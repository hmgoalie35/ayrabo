from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic


class ScorekeepersCreateView(LoginRequiredMixin, generic.View):
    pass
