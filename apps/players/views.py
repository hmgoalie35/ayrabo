from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, Http404, redirect
from django.urls import reverse
from django.views import generic
from django.views.generic.base import ContextMixin

from escoresheet.utils import email_admins_sport_not_configured
from escoresheet.utils.exceptions import SportNotConfiguredException
from escoresheet.utils.mixins import AccountAndSportRegistrationCompleteMixin
from sports.models import SportRegistration
from .forms import HockeyPlayerForm, BaseballPlayerForm, BasketballPlayerForm, PlayerModelFormSet
from .formset_helpers import HockeyPlayerFormSetHelper, BaseballPlayerFormSetHelper
from .models import HockeyPlayer, BasketballPlayer, BaseballPlayer

SPORT_PLAYER_FORM_MAPPINGS = {
    'Ice Hockey': HockeyPlayerForm,
    'Baseball': BaseballPlayerForm,
    'Basketball': BasketballPlayerForm
}

SPORT_PLAYER_MODEL_MAPPINGS = {
    'Ice Hockey': HockeyPlayer,
    'Basketball': BasketballPlayer,
    'Baseball': BaseballPlayer
}

SPORT_PLAYER_FORMSET_HELPER_MAPPINGS = {
    'Ice Hockey': HockeyPlayerFormSetHelper,
    'Basketball': BasketballPlayer,
    'Baseball': BaseballPlayerFormSetHelper
}


class CreatePlayersView(LoginRequiredMixin, ContextMixin, AccountAndSportRegistrationCompleteMixin, generic.View):
    template_name = 'players/players_create.html'

    def _handle_sport_not_configured(self, e):
        email_admins_sport_not_configured(e.sport, self)
        return render(self.request, 'sport_not_configured_msg.html', {'message': e.message})

    def get_context_data(self, **kwargs):
        context = super(CreatePlayersView, self).get_context_data(**kwargs)

        sr = get_object_or_404(SportRegistration.objects.select_related('sport'), pk=kwargs.get('pk'))
        # Make sure sr isn't complete?
        if sr.user_id != self.request.user.id:
            raise Http404

        sport_name = sr.sport.name

        form_cls = SPORT_PLAYER_FORM_MAPPINGS.get(sport_name)
        model_cls = SPORT_PLAYER_MODEL_MAPPINGS.get(sport_name)
        formset_helper_cls = SPORT_PLAYER_FORMSET_HELPER_MAPPINGS.get(sport_name)
        if form_cls is None or model_cls is None or formset_helper_cls is None:
            raise SportNotConfiguredException(sport_name)

        PlayerFormSet = forms.modelformset_factory(model_cls, form=form_cls, formset=PlayerModelFormSet, extra=0,
                                                   min_num=1, max_num=10, validate_min=True, validate_max=True,
                                                   can_delete=False)
        context['formset'] = PlayerFormSet(self.request.POST or None, queryset=model_cls.objects.none(),
                                           prefix='players', form_kwargs={'sport': sr.sport})
        context['helper'] = formset_helper_cls
        context['sport_name'] = sport_name
        context['sport_registration'] = sr
        return context

    def get(self, *args, **kwargs):
        try:
            context = self.get_context_data(**kwargs)
        except SportNotConfiguredException as e:
            return self._handle_sport_not_configured(e)

        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):
        try:
            context = self.get_context_data(**kwargs)
        except SportNotConfiguredException as e:
            return self._handle_sport_not_configured(e)

        formset = context.get('formset')
        sport_registration = context.get('sport_registration')
        user = self.request.user
        for form in formset:
            form.instance.user = user
            form.instance.sport = sport_registration.sport
        if formset.is_valid():
            formset.save()
            next_role = sport_registration.get_next_namespace_for_registration()
            if next_role is None:
                # No remaining roles need to be filled out for this sport registration, mark as complete.
                sport_registration.is_complete = True
                sport_registration.save()
                # See if there are remaining incomplete sport registrations.
                next_sr = self.request.session.pop('next_sport_registration', None)
                if next_sr is not None:
                    next_sr_id = next_sr.get('id')
                    next_sr_role = next_sr.get('role')
                    url = 'sportregistrations:{role}:create'.format(role=next_sr_role)
                    return redirect(reverse(url, kwargs={'pk': next_sr_id}))
                # All incomplete sport registrations have been completed.
                return redirect('home')
            else:
                url = 'sportregistrations:{role}:create'.format(role=next_role)
                return redirect(reverse(url, kwargs={'pk': sport_registration.id}))
        return render(self.request, self.template_name, context)
