from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import Http404, get_object_or_404, redirect, render
from django.views import generic
from django.views.generic import base

from coaches.models import Coach
from sports.models import SportRegistration
from . import forms


class CoachesUpdateView(LoginRequiredMixin, base.ContextMixin, generic.View):
    template_name = 'coaches/coaches_update.html'

    def _get_sport_registration(self):
        return get_object_or_404(SportRegistration, pk=self.kwargs.get('pk', None))

    def _get_coach(self):
        return get_object_or_404(Coach, pk=self.kwargs.get('coach_pk', None))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sport_registration = self._get_sport_registration()
        coach = self._get_coach()

        user_id = self.request.user.id
        if user_id != sport_registration.user_id or user_id != coach.user_id:
            raise Http404

        context['sport_registration'] = sport_registration
        context['coach'] = coach
        context['form'] = forms.CoachUpdateForm(self.request.POST or None, instance=coach)
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = context.get('form')
        sr = context.get('sport_registration')
        if form.is_valid():
            if form.has_changed():
                form.save()
                messages.success(request, 'Your coach information has been updated.')
            return redirect(sr.get_absolute_url())
        return render(request, self.template_name, context)
