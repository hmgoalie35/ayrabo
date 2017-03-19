from collections import OrderedDict

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.views.generic.base import ContextMixin

from coaches import forms as coach_forms
from coaches.models import Coach
from escoresheet.utils.mixins import AccountAndSportRegistrationCompleteMixin
from managers import forms as manager_forms
from managers.models import Manager
from players import forms as player_forms
from players.models import HockeyPlayer, BasketballPlayer, BaseballPlayer
from referees import forms as referee_forms
from referees.models import Referee
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


# TODO Add API endpoints to do this, so don't have to deal with the formset stuff
class CreateSportRegistrationView(LoginRequiredMixin, ContextMixin, AccountAndSportRegistrationCompleteMixin,
                                  generic.View):
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
                                                              min_num=1, max_num=remaining_sport_count,
                                                              validate_min=True, validate_max=True, can_delete=False)

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
        sport_registrations = []
        if formset.is_valid():
            for form in formset:
                # Since I am not using formset.save(), any empty added forms pass validation but fail on .save()
                # because a sport has not been chosen. So this check makes sure the form actually had data submitted.
                if form.cleaned_data:
                    form.instance.user = request.user
                    form.instance.set_roles(form.cleaned_data.get('roles', []))
                    sr = form.save()
                    sport_registrations.append(sr)
            first_sport_reg = sport_registrations[0]
            namespace_for_role = first_sport_reg.get_next_namespace_for_registration()
            url = 'sportregistrations:{role}:create'.format(role=namespace_for_role)
            return redirect(reverse(url, kwargs={'pk': first_sport_reg.id}))

        return render(request, self.template_name, context)


class SportRegistrationDetailView(LoginRequiredMixin, ContextMixin, generic.View):
    template_name = 'sports/sport_registration_detail.html'

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
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)


class AddSportRegistrationRoleView(LoginRequiredMixin, ContextMixin, generic.View):
    template_name = 'sports/sport_registration_add_role.html'
    success_message = '{role} role successfully added to {sport}.'

    def get_context_data(self, **kwargs):
        context = super(AddSportRegistrationRoleView, self).get_context_data(**kwargs)
        sr = get_object_or_404(SportRegistration.objects.select_related('sport'), pk=kwargs.get('pk', None))
        if sr.user_id != self.request.user.id:
            raise Http404
        form_class = None
        role = kwargs.get('role', None)
        sport = sr.sport
        # This variable is used to determine if a coach, referee, etc. object has already been created for this
        # user and sport this is possible because a user can unregister for a role and then re-register for
        # that role again.
        related_role_object = None
        if role == 'player':
            form_class = SPORT_PLAYER_FORM_MAPPINGS[sport.name]
            model_class = SPORT_PLAYER_MODEL_MAPPINGS.get(sport.name)
            related_role_object = model_class.objects.filter(user=self.request.user, sport=sport).first()
        elif role == 'coach':
            form_class = coach_forms.CoachForm
            related_role_object = Coach.objects.filter(user=self.request.user,
                                                       team__division__league__sport=sport).first()
        elif role == 'referee':
            form_class = referee_forms.RefereeForm
            related_role_object = Referee.objects.filter(user=self.request.user, league__sport=sport).first()
        elif role == 'manager':
            form_class = manager_forms.ManagerForm
            related_role_object = Manager.objects.filter(user=self.request.user,
                                                         team__division__league__sport=sport).first()

        # Show the user the object they had previously created for the given sport.
        form_kwargs = {}
        if related_role_object:
            form_kwargs['instance'] = related_role_object
            form_kwargs['read_only_fields'] = ['__all__']

        form = form_class(self.request.POST or None, sport=sport, **form_kwargs)

        context['related_role_object'] = related_role_object
        context['form'] = form
        context['role'] = role
        context['sport_registration'] = sr
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        sr = context.get('sport_registration')
        role = context.get('role')
        if sr.has_role(role):
            messages.info(request, 'You are already registered as a {role}.'.format(role=role))
            return redirect(sr.get_absolute_url())
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = context.get('form', None)
        role = context.get('role', None)
        sr = context.get('sport_registration', None)
        if sr.has_role(role):
            messages.info(request, 'You are already registered as a {role}.'.format(role=role))
            return redirect(sr.get_absolute_url())
        form.instance.user = request.user
        form.instance.sport_id = sr.sport_id

        # NOTE player, coach, etc. objects check to make sure the sport registration has the specified role in
        # the .clean method, so set the role before saving the object so this check is valid
        sr.set_roles([role.title()], append=True)

        if context.get('related_role_object', None) is not None:
            messages.success(request, self.success_message.format(role=role.title(), sport=sr.sport))
            return redirect(sr.get_absolute_url())

        if form.is_valid():
            form.save()
            messages.success(request, self.success_message.format(role=role.title(), sport=sr.sport))
            return redirect(sr.get_absolute_url())
        # Remove the role that was added if the form wasn't valid.
        sr.remove_role(role)
        return render(request, self.template_name, context)
