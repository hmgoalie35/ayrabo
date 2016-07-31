from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import redirect, render
from django.views.generic import CreateView, UpdateView, View
from django.views.generic.base import ContextMixin

from coaches.forms import CoachForm
from managers.forms import ManagerForm
from players.forms import HockeyPlayerForm, BaseballPlayerForm, BasketballPlayerForm
from referees.forms import RefereeForm
from userprofiles.models import UserProfile, RolesMask
from .forms import CreateUserProfileForm, UpdateUserProfileForm, RolesMaskForm


def check_account_completed(request):
    """
    This helper function performs the same thing as the middleware, but because the middleware lets the whitelisted
    urls through, we need to do the check again in the actual view.
    :param request: The request object passed to the view
    :return: redirect_url: The url to redirect to, redirect_needed: If the redirect needs to happen
    """
    # These checks are needed because the middleware allows through any request from the whitelisted urls
    up = UserProfile.objects.filter(user=request.user)
    roles_not_set = RolesMask.objects.filter(user=request.user, are_roles_set=False)
    objects_not_created = RolesMask.objects.filter(user=request.user, are_role_objects_created=False)
    redirect_url = None
    if not up.exists():
        redirect_url = reverse('profile:create')
    elif roles_not_set.exists():
        redirect_url = reverse('profile:select_roles')
    elif objects_not_created.exists():
        redirect_url = reverse('profile:finish')
    # The latter part of this statement prevents redirect loops
    redirect_needed = redirect_url is not None and request.path != redirect_url
    return redirect_url, redirect_needed


class CreateUserProfileView(LoginRequiredMixin, CreateView):
    model = UserProfile
    template_name = 'userprofiles/create.html'
    success_url = reverse_lazy('profile:select_roles')
    form_class = CreateUserProfileForm

    def get(self, request, *args, **kwargs):
        redirect_url, redirect_needed = check_account_completed(request)
        if redirect_needed:
            return redirect(redirect_url)
        return super(CreateUserProfileView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        redirect_url, redirect_needed = check_account_completed(request)
        if redirect_needed:
            return redirect(redirect_url)
        return super(CreateUserProfileView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
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
        incomplete_roles_masks = RolesMask.objects.filter(user=self.request.user,
                                                          are_roles_set=False).select_related('sport')
        roles_mask_count = incomplete_roles_masks.count()
        context['remaining_roles_masks'] = roles_mask_count
        context['incomplete_roles_masks_exist'] = incomplete_roles_masks.exists()
        if context.get('incomplete_roles_masks_exist'):
            incomplete_mask = incomplete_roles_masks.first()
            context['sport_name'] = incomplete_mask.sport.name
            context['form'] = RolesMaskForm(self.request.POST or None, initial=incomplete_mask)
        return context

    def get(self, request, *args, **kwargs):
        redirect_url, redirect_needed = check_account_completed(request)
        if redirect_needed:
            return redirect(redirect_url)
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        redirect_url, redirect_needed = check_account_completed(request)
        if redirect_needed:
            return redirect(redirect_url)
        context = self.get_context_data(**kwargs)
        form = context.get('form')
        if form.is_valid():
            # The set_roles function sets are_roles_set to True when it is called
            form.initial.set_roles(form.cleaned_data.get('roles'), [])
            form.initial.save()
            return redirect(reverse('profile:select_roles'))

        return render(request, self.template_name, context)


class FinishUserProfileView(LoginRequiredMixin, ContextMixin, View):
    template_name = 'userprofiles/finish_profile.html'
    success_message = 'You have successfully completed your profile, you can now access the site'
    sport_player_form_mappings = {
        'Ice Hockey': HockeyPlayerForm,
        'Baseball': BaseballPlayerForm,
        'Basketball': BasketballPlayerForm
    }

    def get_context_data(self, **kwargs):
        context = super(FinishUserProfileView, self).get_context_data(**kwargs)
        roles_masks = RolesMask.objects.filter(user=self.request.user, are_roles_set=True,
                                               are_role_objects_created=False).select_related('sport')
        context['roles_masks_exist'] = roles_masks.exists()
        context['remaining_roles_masks'] = roles_masks.count()
        if context.get('roles_masks_exist'):
            rm = roles_masks.first()
            context['roles_mask'] = rm
            context['sport_name'] = rm.sport.name
            if rm.has_role('Coach'):
                context['coach_form'] = CoachForm(self.request.POST or None)
            if rm.has_role('Player'):
                # Devs have to manually add in the form class to the sport_player_form_mappings dictionary
                # This is because each sport has a different player model, there is no generic player model
                if rm.sport.name not in self.sport_player_form_mappings:
                    raise Exception(
                            "Form class for a {sport} player hasn't been configured yet, add it to sport_player_form_mappings".format(
                                    sport=rm.sport.name))
                context['player_form'] = self.sport_player_form_mappings[rm.sport.name](self.request.POST or None)
            if rm.has_role('Manager'):
                context['manager_form'] = ManagerForm(self.request.POST or None)
            if rm.has_role('Referee'):
                context['referee_form'] = RefereeForm(self.request.POST or None)
        return context

    def get(self, request, *args, **kwargs):
        redirect_url, redirect_needed = check_account_completed(request)
        if redirect_needed:
            return redirect(redirect_url)

        context = self.get_context_data(**kwargs)

        if not context.get('roles_masks_exist'):
            messages.success(request, self.success_message)
            return redirect(reverse('home'))

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        redirect_url, redirect_needed = check_account_completed(request)
        if redirect_needed:
            return redirect(redirect_url)

        context = self.get_context_data(**kwargs)

        if not context.get('roles_masks_exist'):
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
        rm = context.get('roles_mask')
        rm.are_role_objects_created = True
        rm.save()
        return redirect(reverse('profile:finish'))


class UpdateUserProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UserProfile
    form_class = UpdateUserProfileForm
    template_name = 'userprofiles/update.html'
    success_url = reverse_lazy('profile:update')
    success_message = 'Your profile has been updated'
    context_object_name = 'userprofile'

    def get_object(self, queryset=None):
        return self.request.user.userprofile

    def form_valid(self, form):
        if form.has_changed():
            return super(UpdateUserProfileView, self).form_valid(form)
        else:
            return redirect(reverse('profile:update'))
