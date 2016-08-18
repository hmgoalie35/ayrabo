from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.views import generic
from django.views.generic.base import ContextMixin

from coaches import forms as coach_forms
from managers import forms as manager_forms
from players import forms as player_forms
from referees import forms as referee_forms
from userprofiles.views import check_account_and_sport_registration_completed
from .forms import CreateSportRegistrationForm
from .models import SportRegistration, Sport


class FinishSportRegistrationView(LoginRequiredMixin, ContextMixin, generic.View):
    template_name = 'sports/sport_registration_finish.html'
    success_message_account_registration_complete = 'Your profile is now complete, you may now access the site'
    success_message_sport_registrations_finished = 'You have finished registering for {sports}.'
    sport_player_form_mappings = {
        'Ice Hockey': player_forms.HockeyPlayerForm,
        'Baseball': player_forms.BaseballPlayerForm,
        'Basketball': player_forms.BasketballPlayerForm
    }

    def get_context_data(self, **kwargs):
        context = super(FinishSportRegistrationView, self).get_context_data(**kwargs)
        sport_registrations = SportRegistration.objects.filter(user=self.request.user,
                                                               is_complete=False).select_related('sport')
        context['sport_registrations_exist'] = sport_registrations.exists()
        context['remaining_sport_registrations'] = sport_registrations.count()
        if context.get('sport_registrations_exist'):
            sr = sport_registrations.first()
            context['sport_registration'] = sr
            context['sport_name'] = sr.sport.name
            if 'sports_registered_for' in self.request.session.keys():
                if sr.sport.name not in self.request.session.get('sports_registered_for'):
                    self.request.session.get('sports_registered_for').append(sr.sport.name)
            else:
                self.request.session['sports_registered_for'] = [sr.sport.name]
            if sr.has_role('Coach'):
                context['coach_form'] = coach_forms.CoachForm(self.request.POST or None, sport=sr.sport)
            if sr.has_role('Player'):
                # Devs have to manually add in the form class to the sport_player_form_mappings dictionary
                # This is because each sport has a different player model, there is no generic player model
                if sr.sport.name not in self.sport_player_form_mappings:
                    raise Exception(
                            "Form class for a {sport} player hasn't been configured yet, add it to sport_player_form_mappings".format(
                                    sport=sr.sport.name))
                context['player_form'] = self.sport_player_form_mappings[sr.sport.name](self.request.POST or None,
                                                                                        sport=sr.sport)
            if sr.has_role('Manager'):
                context['manager_form'] = manager_forms.ManagerForm(self.request.POST or None, sport=sr.sport)
            if sr.has_role('Referee'):
                context['referee_form'] = referee_forms.RefereeForm(self.request.POST or None, sport=sr.sport)
        return context

    def get(self, request, *args, **kwargs):
        redirect_url, redirect_needed = check_account_and_sport_registration_completed(request)
        if redirect_needed:
            return redirect(redirect_url)

        context = self.get_context_data(**kwargs)

        if not context.get('sport_registrations_exist'):
            sports_registered_for = request.session.get('sports_registered_for', None)
            if sports_registered_for:
                messages.success(request, self.success_message_sport_registrations_finished.format(
                        sports=', '.join(sports_registered_for)))
                if request.session.get('is_user_currently_registering', False):
                    messages.success(request, self.success_message_account_registration_complete)
            return redirect(reverse('home'))

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        redirect_url, redirect_needed = check_account_and_sport_registration_completed(request)
        if redirect_needed:
            return redirect(redirect_url)

        context = self.get_context_data(**kwargs)

        if not context.get('sport_registrations_exist'):
            sports_registered_for = request.session.get('sports_registered_for', None)
            if sports_registered_for:
                messages.success(request, self.success_message_sport_registrations_finished.format(
                        sports=', '.join(sports_registered_for)))
                if request.session.get('is_user_currently_registering', False):
                    messages.success(request, self.success_message_account_registration_complete)
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


class SportRegistrationInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super(SportRegistrationInlineFormSet, self).clean()
        sports_already_seen = []
        for form in self.forms:
            sport = form.cleaned_data.get('sport')
            if sport is not None:
                if sport in sports_already_seen:
                    form.add_error('sport',
                                   'Only one form can have {sport} selected. Choose another sport, or the "---------" value.'.format(
                                           sport=sport.name))
                else:
                    sports_already_seen.append(sport)


class CreateSportRegistrationView(LoginRequiredMixin, ContextMixin, generic.View):
    template_name = 'sports/sport_registration_create.html'
    already_registered_msg = 'You have already registered for all available sports. Check back later to see if any new sports have been added.'
    success_msg = 'You have successfully registered for {sports}.'

    def get_context_data(self, **kwargs):
        context = super(CreateSportRegistrationView, self).get_context_data(**kwargs)
        sports_already_registered_for = SportRegistration.objects.filter(user=self.request.user).values_list('sport_id')
        context['remaining_sport_count'] = Sport.objects.count() - len(sports_already_registered_for)
        context['user_registered_for_all_sports'] = context.get('remaining_sport_count') == 0
        sport_registration_form_set = inlineformset_factory(User, SportRegistration, form=CreateSportRegistrationForm,
                                                            formset=SportRegistrationInlineFormSet,
                                                            extra=0,
                                                            min_num=1, max_num=context.get('remaining_sport_count'),
                                                            validate_min=True, validate_max=True, can_delete=False)
        context['formset'] = sport_registration_form_set(self.request.POST or None,
                                                         form_kwargs={
                                                             'sports_already_registered_for': sports_already_registered_for})
        return context

    def get(self, request, *args, **kwargs):
        redirect_url, redirect_needed = check_account_and_sport_registration_completed(request)
        if redirect_needed:
            return redirect(redirect_url)
        context = self.get_context_data(**kwargs)
        if context.get('user_registered_for_all_sports'):
            messages.info(request, self.already_registered_msg)
            return redirect(request.META.get('HTTP_REFERER', '/'))
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        redirect_url, redirect_needed = check_account_and_sport_registration_completed(request)
        if redirect_needed:
            return redirect(redirect_url)

        context = self.get_context_data(**kwargs)

        if context.get('user_registered_for_all_sports'):
            messages.info(request, self.already_registered_msg)
            return redirect(reverse('home'))

        formset = context.get('formset')
        if formset.is_valid():
            sports_registered_for = []
            for form in formset.forms:
                # Since I am not using formset.save(), any empty added forms pass validation but fail on .save()
                # because a sport has not been chosen. So this check makes sure the form actually had data submitted.
                if form.cleaned_data:
                    form.instance.user = request.user
                    form.instance.set_roles(form.cleaned_data.get('roles', []))
                    form.save()
                    sports_registered_for.append(form.instance.sport.name)
            if sports_registered_for:
                messages.success(request, self.success_msg.format(sports=', '.join(sports_registered_for)))
            return redirect(reverse('sport:finish_sport_registration'))

        return render(request, self.template_name, context)


class UpdateSportRegistrationView(LoginRequiredMixin, ContextMixin, generic.View):
    template_name = 'sports/sport_registration_update.html'
    sport_player_form_mappings = {
        'Ice Hockey': player_forms.HockeyPlayerForm,
        'Baseball': player_forms.BaseballPlayerForm,
        'Basketball': player_forms.BasketballPlayerForm
    }

    def get_context_data(self, **kwargs):
        context = super(UpdateSportRegistrationView, self).get_context_data(**kwargs)
        sr = get_object_or_404(SportRegistration, pk=kwargs.get('pk', None))
        if sr.user != self.request.user:
            context['not_obj_owner'] = True
            return context
        context['sport_registration'] = sr
        related_objects = sr.get_related_role_objects()
        context['player_read_only_fields'] = ['team']
        context['coach_read_only_fields'] = ['team']
        context['manager_read_only_fields'] = ['team']
        context['referee_read_only_fields'] = ['league']
        for role, role_obj in related_objects.items():
            if role == 'Player':
                context['player_form'] = self.sport_player_form_mappings[sr.sport.name](self.request.POST or None,
                                                                                        instance=role_obj,
                                                                                        read_only_fields=context.get(
                                                                                                'player_read_only_fields'))
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
        context = self.get_context_data(**kwargs)
        if context.get('not_obj_owner'):
            raise Http404
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if context.get('not_obj_owner'):
            raise Http404
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
