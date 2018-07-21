from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import generic
from django.views.generic.base import ContextMixin

from ayrabo.utils.mixins import HasPermissionMixin
from players import forms as player_forms
from players.models import BaseballPlayer, BasketballPlayer, HockeyPlayer
from scorekeepers.models import Scorekeeper
from sports.forms import SportRegistrationCreateForm, SportRegistrationFormSet
from sports.formset_helpers import SportRegistrationCreateFormSetHelper
from sports.models import Sport, SportRegistration

SPORT_PLAYER_FORM_MAPPINGS = {
    'Ice Hockey': player_forms.HockeyPlayerForm,
    'Baseball': player_forms.BaseballPlayerForm,
    'Basketball': player_forms.BasketballPlayerForm
}

SPORT_PLAYER_MODEL_MAPPINGS = {
    'Ice Hockey': HockeyPlayer,
    'Basketball': BasketballPlayer,
    'Baseball': BaseballPlayer
}


class SportRegistrationCreateView(LoginRequiredMixin, HasPermissionMixin, ContextMixin, generic.View):
    form_class = SportRegistrationCreateForm
    formset_class = SportRegistrationFormSet
    min_forms = 1
    extra = 0
    template_name = 'sports/sport_registration_create.html'

    def has_permission_func(self):
        user = self.request.user
        # .distinct('sport_id') doesn't work on sqlite. Use a set instead of list here because sets are unique.
        self.sports_already_registered_for = {sr.sport.id for sr in
                                              user.sport_registrations.all().select_related('sport')}
        # This should never be negative
        self.remaining_sport_count = Sport.objects.count() - len(self.sports_already_registered_for)
        return self.remaining_sport_count > 0

    def on_has_permission_failure(self):
        messages.info(self.request, 'You have already registered for all available sports.')
        redirect_url = self.request.META.get('HTTP_REFERER', reverse('home'))
        return redirect(redirect_url)

    def get_form_class(self):
        return self.form_class

    def get_form_kwargs(self):
        return {}

    def get_formset_factory(self):
        """
        This function needs to return the formset factory directly, returning a class variable assigned to the formset
        factory wasn't working.
        """
        return forms.formset_factory

    def get_formset_class(self):
        return self.formset_class

    def get_formset_kwargs(self):
        formset_kwargs = {
            'formset': self.get_formset_class(),
            'form': self.get_form_class(),
            'extra': self.extra,
            'min_num': self.min_forms,
            'validate_min': True,
            'validate_max': True,
            'can_delete': False
        }
        return formset_kwargs

    def get_formset(self, formset_kwargs=None, form_kwargs=None):
        _formset_kwargs = self.get_formset_kwargs()
        if formset_kwargs:
            _formset_kwargs.update(formset_kwargs)

        _form_kwargs = self.get_form_kwargs()
        if form_kwargs:
            _form_kwargs.update(form_kwargs)

        FormSet = self.get_formset_factory()(**_formset_kwargs)
        return FormSet(
            data=self.request.POST or None,
            files=self.request.FILES or None,
            prefix='sportregistrations',
            form_kwargs=_form_kwargs
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = self.get_formset(
            formset_kwargs={'max_num': self.remaining_sport_count},
            form_kwargs={'sports_already_registered_for': self.sports_already_registered_for}
        )
        context['helper'] = SportRegistrationCreateFormSetHelper
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)

    def handle_scorekeeper_role(self, user, sport):
        return Scorekeeper.objects.create(user=user, sport=sport)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        formset = context.get('formset')
        user = request.user

        if formset.is_valid():
            sport_names = []
            # A formset is still valid even if there are empty forms so remove the empty forms before processing.
            valid_forms = [form for form in formset if form.cleaned_data]
            for form in valid_forms:
                sport = form.cleaned_data.get('sport')
                roles = form.cleaned_data.get('roles')
                SportRegistration.objects.create_for_user_and_sport(user, sport, roles)
                if 'scorekeeper' in roles:
                    self.handle_scorekeeper_role(user, sport)
                sport_names.append(sport.name)
            messages.success(request, 'You have been registered for {}.'.format(', '.join(sport_names)))
            return redirect(reverse('home'))

        return render(request, self.template_name, context)
