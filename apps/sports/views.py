from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Field, Div
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
from escoresheet.utils import email_admins_sport_not_configured
from escoresheet.utils.exceptions import SportNotConfiguredException
from escoresheet.utils.mixins import AccountAndSportRegistrationCompleteMixin
from managers import forms as manager_forms
from managers.models import Manager
from players import forms as player_forms
from players.models import HockeyPlayer, BasketballPlayer, BaseballPlayer
from referees import forms as referee_forms
from referees.models import Referee
from .forms import CreateSportRegistrationForm
from .models import SportRegistration, Sport

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


class FinishSportRegistrationView(LoginRequiredMixin, ContextMixin, AccountAndSportRegistrationCompleteMixin,
                                  generic.View):
    template_name = 'sports/sport_registration_finish.html'
    success_msg = 'You are now registered for {sports}.'

    def _handle_sport_not_configured(self, e):
        email_admins_sport_not_configured(e.sport, self)
        return render(self.request, 'sport_not_configured_msg.html', {'message': e.message})

    def get_context_data(self, **kwargs):
        context = super(FinishSportRegistrationView, self).get_context_data(**kwargs)
        sport_registrations = SportRegistration.objects.filter(user=self.request.user,
                                                               is_complete=False).select_related('sport')
        sport_registrations_exist = sport_registrations.exists()
        if sport_registrations_exist:
            sr = sport_registrations.first()
            sport_name = sr.sport.name
            context['sport_registration'] = sr
            context['sport_name'] = sport_name
            if 'sports_registered_for' in self.request.session.keys():
                if sport_name not in self.request.session.get('sports_registered_for'):
                    self.request.session.get('sports_registered_for').append(sport_name)
            else:
                self.request.session['sports_registered_for'] = [sport_name]
            if sr.has_role('Coach'):
                context['coach_form'] = coach_forms.CoachForm(self.request.POST or None, sport=sr.sport)
            if sr.has_role('Player'):
                form_cls = SPORT_PLAYER_FORM_MAPPINGS.get(sport_name)
                if form_cls is None:
                    raise SportNotConfiguredException(sport_name)
                player_form = form_cls(self.request.POST or None, sport=sr.sport)
                context['player_form'] = player_form
            if sr.has_role('Manager'):
                context['manager_form'] = manager_forms.ManagerForm(self.request.POST or None, sport=sr.sport)
            if sr.has_role('Referee'):
                context['referee_form'] = referee_forms.RefereeForm(self.request.POST or None, sport=sr.sport)

            context['sport_registrations_remaining'] = [sr.sport.name for sr in sport_registrations if
                                                        sr.sport.name != sport_name]

        context['sport_registrations_exist'] = sport_registrations_exist
        return context

    def get(self, request, *args, **kwargs):
        try:
            context = self.get_context_data(**kwargs)
        except SportNotConfiguredException as e:
            return self._handle_sport_not_configured(e)

        if not context.get('sport_registrations_exist'):
            sports_registered_for = request.session.pop('sports_registered_for', None)
            if sports_registered_for:
                messages.success(request, self.success_msg.format(
                        sports=', '.join(sports_registered_for)))
            return redirect(reverse('home'))

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        try:
            context = self.get_context_data(**kwargs)
        except SportNotConfiguredException as e:
            return self._handle_sport_not_configured(e)

        if not context.get('sport_registrations_exist'):
            sports_registered_for = request.session.pop('sports_registered_for', None)
            if sports_registered_for:
                messages.success(request, self.success_msg.format(
                        sports=', '.join(sports_registered_for)))
            return redirect(reverse('home'))

        # Forms that were submitted are added to this list. Only check the forms in this list for validity
        forms_that_were_submitted = []
        # If a form was submitted and is_valid is True, the corresponding value will be set to True
        is_form_valid = {}

        coach_form = context.get('coach_form', None)
        player_form = context.get('player_form', None)
        manager_form = context.get('manager_form', None)
        referee_form = context.get('referee_form', None)
        user = request.user

        if coach_form is not None:
            forms_that_were_submitted.append(coach_form)
            coach_form.instance.user = user
            is_form_valid[coach_form] = coach_form.is_valid()

        if manager_form is not None:
            forms_that_were_submitted.append(manager_form)
            manager_form.instance.user = user
            is_form_valid[manager_form] = manager_form.is_valid()

        if referee_form is not None:
            forms_that_were_submitted.append(referee_form)
            referee_form.instance.user = user
            is_form_valid[referee_form] = referee_form.is_valid()

        if player_form is not None:
            forms_that_were_submitted.append(player_form)
            is_form_valid[player_form] = False
            player_form.instance.user = user
            if player_form.is_valid():
                player_form.instance.sport = player_form.instance.team.division.league.sport
                is_form_valid[player_form] = True

        # Check to see if all of the forms that were submitted are valid.
        # If there is a non valid form that was submitted, redisplay the form with errors
        for submitted_form in forms_that_were_submitted:
            if not is_form_valid[submitted_form]:
                return render(request, self.template_name, context)

        # Need to make sure all submitted forms were valid before saving them, otherwise will have a bug where
        # submitting a valid form for coach will create the object but any other invalid form will throw an error. When
        # the user tries to resubmit the forms then will have integrity error because coach object was already created
        for form, is_valid in is_form_valid.items():
            if is_valid:
                form.save()
        sr = context.get('sport_registration')
        sr.is_complete = True
        sr.save()
        return redirect(reverse('sport:finish_sport_registration'))


class SportRegistrationModelFormSet(forms.BaseModelFormSet):
    def add_fields(self, form, index):
        super(SportRegistrationModelFormSet, self).add_fields(form, index)
        # The empty form would have value `None`, so default to an invalid form_num for use in the js.
        form_num = index if index is not None else -1
        form.fields['form_num'] = forms.IntegerField(required=False, widget=forms.HiddenInput(
                attrs={'data-form-num': form_num, 'class': 'form-num'}))

    def clean(self):
        super(SportRegistrationModelFormSet, self).clean()
        sports_already_seen = []
        for form in self.forms:
            sport = form.cleaned_data.get('sport')
            if sport is not None:
                if sport in sports_already_seen:
                    form.add_error('sport', 'Only one form can have {sport} selected. '
                                            'Choose another sport, or remove this form.'.format(sport=sport.name))
                else:
                    sports_already_seen.append(sport)


class CreateSportRegistrationFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(CreateSportRegistrationFormSetHelper, self).__init__(*args, **kwargs)
        self.layout = Layout(
                Div(
                        HTML(
                                "{% if not forloop.first %}<span data-toggle=\"tooltip\" data-placement=\"top\" "
                                "title=\"Remove form\" class=\"fa fa-trash fa-trash-red pull-right\"></span>{% endif %}"
                        ),
                        Field('sport'),
                        Field('roles'),
                        Field('form_num'),
                        Field('id'),
                        css_class="multiField"
                )
        )
        self.form_tag = False
        # csrf token is added in the template
        self.disable_csrf = True


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
        if formset.is_valid():
            for form in formset:
                # Since I am not using formset.save(), any empty added forms pass validation but fail on .save()
                # because a sport has not been chosen. So this check makes sure the form actually had data submitted.
                if form.cleaned_data:
                    form.instance.user = request.user
                    form.instance.set_roles(form.cleaned_data.get('roles', []))
                    form.save()
            return redirect(reverse('sport:finish_sport_registration'))

        return render(request, self.template_name, context)


class UpdateSportRegistrationView(LoginRequiredMixin, ContextMixin, generic.View):
    template_name = 'sports/sport_registration_update.html'

    def _handle_sport_not_configured(self, e):
        email_admins_sport_not_configured(e.sport, self)
        return render(self.request, 'sport_not_configured_msg.html', {'message': e.message})

    def get_context_data(self, **kwargs):
        context = super(UpdateSportRegistrationView, self).get_context_data(**kwargs)
        sr = get_object_or_404(SportRegistration.objects.select_related('sport'), pk=kwargs.get('pk', None))
        if sr.user_id != self.request.user.id:
            raise Http404
        sport_name = sr.sport.name
        context['sport_name'] = sport_name
        context['sport_registration'] = sr
        related_objects = sr.get_related_role_objects()
        context['remaining_roles'] = sorted(set(SportRegistration.ROLES) - set(sr.roles))
        # Used to disable remove role links
        context['has_one_role'] = len(sr.roles) == 1
        context['player_read_only_fields'] = ['team']
        context['coach_read_only_fields'] = ['team']
        context['manager_read_only_fields'] = ['team']
        context['referee_read_only_fields'] = ['league']
        for role, role_obj in related_objects.items():
            if role == 'Player':
                form_cls = SPORT_PLAYER_FORM_MAPPINGS.get(sport_name)
                if form_cls is None:
                    raise SportNotConfiguredException(sport_name)

                context['player_form'] = form_cls(self.request.POST or None, instance=role_obj,
                                                  read_only_fields=context.get('player_read_only_fields'))
            elif role == 'Coach':
                context['coach_form'] = coach_forms.CoachForm(self.request.POST or None, instance=role_obj,
                                                              read_only_fields=context.get('coach_read_only_fields'))
            elif role == 'Manager':
                context['manager_form'] = manager_forms.ManagerForm(self.request.POST or None, instance=role_obj,
                                                                    read_only_fields=context.get(
                                                                            'manager_read_only_fields'))
            elif role == 'Referee':
                context['referee_form'] = referee_forms.RefereeForm(self.request.POST or None, instance=role_obj,
                                                                    read_only_fields=context.get(
                                                                            'referee_read_only_fields'))
        return context

    def get(self, request, *args, **kwargs):
        try:
            context = self.get_context_data(**kwargs)
        except SportNotConfiguredException as e:
            return self._handle_sport_not_configured(e)

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        try:
            context = self.get_context_data(**kwargs)
        except SportNotConfiguredException as e:
            return self._handle_sport_not_configured(e)

        # Forms that were submitted are added to this list. Only check the forms in this list for validity
        forms_that_were_submitted = []
        # If a form was submitted and is_valid is True, the corresponding value will be set to True
        is_form_valid = {}

        coach_form = context.get('coach_form', None)
        player_form = context.get('player_form', None)
        manager_form = context.get('manager_form', None)
        referee_form = context.get('referee_form', None)

        if coach_form is not None and coach_form.has_changed() and coach_form.changed_data != context.get(
                'coach_read_only_fields', []):
            forms_that_were_submitted.append(coach_form)
            is_form_valid[coach_form] = coach_form.is_valid()

        if manager_form is not None and manager_form.has_changed() and manager_form.changed_data != context.get(
                'manager_read_only_fields', []):
            forms_that_were_submitted.append(manager_form)
            is_form_valid[manager_form] = manager_form.is_valid()

        if referee_form is not None and referee_form.has_changed() and referee_form.changed_data != context.get(
                'referee_read_only_fields', []):
            forms_that_were_submitted.append(referee_form)
            is_form_valid[referee_form] = referee_form.is_valid()

        if player_form is not None and player_form.has_changed() and player_form.changed_data != context.get(
                'player_read_only_fields', []):
            forms_that_were_submitted.append(player_form)
            is_form_valid[player_form] = False
            if player_form.is_valid():
                is_form_valid[player_form] = True

        if len(forms_that_were_submitted) == 0:
            return render(request, self.template_name, context)

        # Check to see if all of the forms that were submitted are valid.
        # If there is a non valid form that was submitted, redisplay the form with errors
        for submitted_form in forms_that_were_submitted:
            if not is_form_valid[submitted_form]:
                return render(request, self.template_name, context)

        # Need to make sure all submitted forms were valid before saving them, otherwise will have a bug where
        # submitting a valid form for coach will create the object but any other invalid form will throw an error. When
        # the user tries to resubmit the forms then will have integrity error because coach object was already created
        for form, is_valid in is_form_valid.items():
            if is_valid:
                form.save()
        messages.success(request, 'Sport registration for {sport} successfully updated.'.format(
                sport=context['sport_registration'].sport.name))
        return redirect(reverse('account_home'))


class AddSportRegistrationRoleView(LoginRequiredMixin, ContextMixin, generic.View):
    template_name = 'sports/sport_registration_add_role.html'
    success_message = '{role} role successfully added to {sport}'

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
