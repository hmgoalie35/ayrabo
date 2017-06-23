from collections import OrderedDict

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.views.generic.base import ContextMixin

from players import forms as player_forms
from players.models import HockeyPlayer, BasketballPlayer, BaseballPlayer
from sports.forms import CreateSportRegistrationForm, SportRegistrationModelFormSet
from sports.formset_helpers import CreateSportRegistrationFormSetHelper
from sports.models import SportRegistration, Sport

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

MIN_FORMS = 1


# TODO Add API endpoints to do this, so don't have to deal with the formset stuff
class CreateSportRegistrationView(LoginRequiredMixin, ContextMixin, generic.View):
    template_name = 'sports/sport_registration_create.html'
    already_registered_msg = 'You have already registered for all available sports. ' \
                             'Check back later to see if any new sports have been added.'

    def get_context_data(self, **kwargs):
        context = super(CreateSportRegistrationView, self).get_context_data(**kwargs)
        sports_already_registered_for = SportRegistration.objects.filter(user=self.request.user).values_list('sport_id')
        remaining_sport_count = Sport.objects.count() - len(sports_already_registered_for)
        SportRegistrationFormSet = forms.modelformset_factory(SportRegistration,
                                                              form=CreateSportRegistrationForm,
                                                              formset=SportRegistrationModelFormSet,
                                                              fields=('sport', 'roles'),
                                                              extra=0,
                                                              min_num=MIN_FORMS,
                                                              max_num=remaining_sport_count,
                                                              validate_min=True,
                                                              validate_max=True,
                                                              can_delete=False)

        context['remaining_sport_count'] = remaining_sport_count
        context['user_registered_for_all_sports'] = context.get('remaining_sport_count') == 0
        context['formset'] = SportRegistrationFormSet(
                self.request.POST or None,
                queryset=SportRegistration.objects.none(),
                prefix='sportregistrations',
                form_kwargs={'sports_already_registered_for': sports_already_registered_for}
        )
        context['helper'] = CreateSportRegistrationFormSetHelper
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if context.get('user_registered_for_all_sports'):
            messages.info(request, self.already_registered_msg)
            return redirect(request.META.get('HTTP_REFERER', '/'))
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if context.get('user_registered_for_all_sports'):
            messages.info(request, self.already_registered_msg)
            return redirect(reverse('home'))

        formset = context.get('formset')
        if formset.is_valid():
            sport_registrations = []
            sport_names = []
            for form in formset:
                # Since I am not using formset.save(), any empty added forms pass validation but fail on .save()
                # because a sport has not been chosen. So this check makes sure the form actually had data submitted.
                if form.cleaned_data:
                    form.instance.user = request.user
                    form.instance.set_roles(form.cleaned_data.get('roles', []))
                    sr = form.save()
                    sport_names.append(sr.sport.name)
                    sport_registrations.append(sr)
            first_sport_reg = sport_registrations[0]
            namespace_for_role = first_sport_reg.get_next_namespace_for_registration()
            url = 'sportregistrations:{role}:create'.format(role=namespace_for_role)
            messages.success(request, 'You have been registered for {}.'.format(', '.join(sport_names)))
            return redirect(reverse(url, kwargs={'pk': first_sport_reg.id}))

        return render(request, self.template_name, context)


class SportRegistrationDetailView(LoginRequiredMixin, ContextMixin, generic.View):
    template_name = 'sports/sport_registration_detail.html'

    def _get_namespace_for_role(self, role):
        mappings = {
            'Player': 'players',
            'Coach': 'coaches',
            'Referee': 'referees',
            'Manager': 'managers'
        }
        return mappings.get(role, None)

    def _get_url_for_role(self, role, **kwargs):
        namespace = self._get_namespace_for_role(role)
        return reverse('sportregistrations:{}:create'.format(namespace), kwargs=kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sr = get_object_or_404(SportRegistration.objects.select_related('sport'), pk=self.kwargs.get('pk', None))
        if sr.user_id != self.request.user.id:
            raise Http404

        sport_name = sr.sport.name
        sr_roles = sorted(sr.roles)
        related_objects = OrderedDict(sorted(sr.get_related_role_objects().items(), key=lambda t: t[0]))
        context['available_roles'] = sorted(set(SportRegistration.ROLES) - set(sr_roles))
        context['sport_registration'] = sr
        context['sr_roles'] = sr_roles
        context['related_objects'] = related_objects
        context['sport_name'] = sport_name
        role_url_mapping = {}
        for role in SportRegistration.ROLES:
            role_url_mapping[role] = self._get_url_for_role(role, pk=sr.pk)
        context['role_url_mapping'] = role_url_mapping
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)
