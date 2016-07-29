from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import redirect, render
from django.views.generic import CreateView, UpdateView, View
from django.views.generic.base import ContextMixin

from coaches.forms import CoachForm
from managers.forms import ManagerForm
from players.forms import HockeyPlayerForm
from referees.forms import RefereeForm
from userprofiles.models import UserProfile, RolesMask
from .forms import CreateUserProfileForm, UpdateUserProfileForm, RolesMaskForm


class CreateUserProfileView(LoginRequiredMixin, CreateView):
    model = UserProfile
    template_name = 'userprofiles/create.html'
    success_url = reverse_lazy('profile:select_roles')
    form_class = CreateUserProfileForm

    def get(self, request, *args, **kwargs):
        if UserProfile.objects.filter(user=request.user).exists():
            return redirect(reverse('home'))
        return super(CreateUserProfileView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if UserProfile.objects.filter(user=request.user).exists():
            return redirect(reverse('home'))
        return super(CreateUserProfileView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
        form.instance.set_roles([])
        sports = form.cleaned_data.get('sports', [])
        for sport in sports:
            # For every sport the user wants to register for, create a roles mask object for the given sport.
            # Later on the actual roles_mask will be updated to reflect the user's desired roles for a given sport.
            RolesMask.objects.get_or_create(user=user, sport=sport)

        return super(CreateUserProfileView, self).form_valid(form)


class SelectRolesView(LoginRequiredMixin, ContextMixin, View):
    template_name = 'userprofiles/select_roles.html'

    def get_context_data(self, **kwargs):
        context = super(SelectRolesView, self).get_context_data(**kwargs)
        incomplete_roles_masks = RolesMask.objects.filter(user=self.request.user, is_complete=False).select_related('sport')
        roles_mask_count = incomplete_roles_masks.count()
        context['remaining_roles_masks'] = roles_mask_count
        context['incomplete_roles_masks_exist'] = incomplete_roles_masks.exists()
        if context.get('incomplete_roles_masks_exist'):
            incomplete_mask = incomplete_roles_masks.first()
            context['sport_name'] = incomplete_mask.sport.name
            context['form'] = RolesMaskForm(self.request.POST or None, initial=incomplete_mask)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if not context.get('incomplete_roles_masks_exist'):
            return redirect(reverse('profile:finish'))

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if not context.get('incomplete_roles_masks_exist'):
            return redirect(reverse('profile:finish'))
        form = context.get('form')
        if form.is_valid():
            form.initial.set_roles(form.cleaned_data.get('roles'), [])
            form.initial.is_complete = True
            form.initial.save()
            return redirect(reverse('profile:select_roles'))

        return render(request, self.template_name, context)


class FinishUserProfileView(LoginRequiredMixin, ContextMixin, View):
    template_name = 'userprofiles/finish_profile.html'
    success_message = 'You have successfully completed your profile, you can now access the site'

    def get_context_data(self, **kwargs):
        """
        Instantiates a blank form, or a form with POST data
        Note that CoachForm, ManagerForm, etc have a prefix field set so that the name attributed on a field is scoped
        to that model, so no issues arise from having fields with the same name in different models
        The form knows what prefixed data to instantiate the form with
        """
        context = super(FinishUserProfileView, self).get_context_data(**kwargs)
        user_roles = self.request.user.userprofile.roles
        if 'Coach' in user_roles:
            context['coach_form'] = CoachForm(self.request.POST or None)
        if 'Player' in user_roles:
            # this needs to perform logic to determine what player form to use.
            context['player_type'] = 'Hockey'
            context['player_form'] = HockeyPlayerForm(self.request.POST or None)
        if 'Manager' in user_roles:
            context['manager_form'] = ManagerForm(self.request.POST or None)
        if 'Referee' in user_roles:
            context['referee_form'] = RefereeForm(self.request.POST or None)
        return context

    def get(self, request, *args, **kwargs):
        # If the user hasn't created a userprofile yet, redirect them to the profile creation page
        if not hasattr(request.user, 'userprofile'):
            return redirect(reverse('profile:create'))
        # If the user has incomplete roles masks (choosing what roles for the sports they chose) then redirect to
        # the page that will prompt them to finish the roles masks
        qs = RolesMask.objects.filter(user=self.request.user, is_complete=False)
        if qs.exists():
            return redirect(reverse('profile:select_roles'))
        # If the user's profile is complete, redirect to the home page so they can start using the site
        if request.user.userprofile.is_complete:
            return redirect(reverse('home'))

        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # If the user hasn't created a userprofile yet, redirect them to the profile creation page
        if not hasattr(request.user, 'userprofile'):
            return redirect(reverse('profile:create'))
        # If the user has incomplete roles masks (choosing what roles for the sports they chose) then redirect to
        # the page that will prompt them to finish the roles masks
        qs = RolesMask.objects.filter(user=self.request.user, is_complete=False)
        if qs.exists():
            return redirect(reverse('profile:select_roles'))
        # If the user's profile is complete, redirect to the home page so they can start using the site
        if request.user.userprofile.is_complete:
            return redirect(reverse('home'))

        context = self.get_context_data(**kwargs)

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

        # Otherwise all forms that were submitted are valid
        user.userprofile.is_complete = True
        user.userprofile.save()
        messages.success(request, self.success_message)
        return redirect(reverse('home'))


class UpdateUserProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UserProfile
    form_class = UpdateUserProfileForm
    template_name = 'userprofiles/update.html'
    success_url = reverse_lazy('profile:update')
    success_message = 'Your profile has been updated'
    context_object_name = 'userprofile'

    def get_context_data(self, **kwargs):
        context = super(UpdateUserProfileView, self).get_context_data(**kwargs)
        context['user_roles'] = ', '.join(self.request.user.userprofile.roles)
        return context

    def get_object(self, queryset=None):
        return self.request.user.userprofile

    def form_valid(self, form):
        if form.has_changed():
            return super(UpdateUserProfileView, self).form_valid(form)
        else:
            return redirect(reverse('profile:update'))
