from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.shortcuts import redirect, render
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
    success_message = 'You have successfully completed your profile, you can now access the site'
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
            messages.success(request, self.success_message)
            return redirect(reverse('home'))

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        redirect_url, redirect_needed = check_account_and_sport_registration_completed(request)
        if redirect_needed:
            return redirect(redirect_url)

        context = self.get_context_data(**kwargs)

        if not context.get('sport_registrations_exist'):
            messages.success(request, self.success_message)
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
            return redirect(reverse('home'))
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
            for form in formset.forms:
                form.instance.user = request.user
                form.instance.set_roles(form.cleaned_data.get('roles', []))
                form.save()
            return redirect(reverse('sport:finish_sport_registration'))

        return render(request, self.template_name, context)
