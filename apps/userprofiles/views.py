from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import redirect, render
from django.views.generic import CreateView, UpdateView, View
from django.views.generic.base import ContextMixin

from coaches.forms import CoachForm
from managers.forms import ManagerForm
from referees.forms import RefereeForm
from userprofiles.models import UserProfile
from .forms import CreateUserProfileForm, UpdateUserProfileForm


class CreateUserProfileView(LoginRequiredMixin, CreateView):
    model = UserProfile
    template_name = 'userprofiles/create.html'
    success_url = reverse_lazy('profile:finish')
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
        form.instance.user = self.request.user
        form.instance.set_roles(form.cleaned_data.get('roles', []))
        return super(CreateUserProfileView, self).form_valid(form)


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
            context['player_form'] = None
        if 'Manager' in user_roles:
            context['manager_form'] = ManagerForm(self.request.POST or None)
        if 'Referee' in user_roles:
            context['referee_form'] = RefereeForm(self.request.POST or None)
        return context

    def get(self, request, *args, **kwargs):
        # only allow not complete profiles
        if request.user.userprofile.is_complete:
            return redirect(reverse('home'))
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # only allow not complete profiles
        if request.user.userprofile.is_complete:
            return redirect(reverse('home'))

        context = self.get_context_data(**kwargs)

        # Forms that were submitted are added to this list. Only check the forms in this list for validity
        forms_that_were_submitted = []
        # If a form was submitted and is_valid is True, the corresponding value will be set to True
        is_form_valid = {'coach_form': False, 'player_form': False, 'manager_form': False, 'referee_form': False}

        coach_form = context.get('coach_form', None)
        player_form = context.get('player_form', None)
        manager_form = context.get('manager_form', None)
        referee_form = context.get('referee_form', None)
        user = request.user

        if coach_form is not None:
            forms_that_were_submitted.append('coach_form')
            coach_form.instance.user = user
            if coach_form.is_valid():
                is_form_valid['coach_form'] = True
                coach_form.save()

        if manager_form is not None:
            forms_that_were_submitted.append('manager_form')
            manager_form.instance.user = user
            if manager_form.is_valid():
                is_form_valid['manager_form'] = True
                manager_form.save()

        if referee_form is not None:
            forms_that_were_submitted.append('referee_form')
            referee_form.instance.user = user
            if referee_form.is_valid():
                is_form_valid['referee_form'] = True
                referee_form.save()

        # Check to see if all of the forms that were submitted are valid.
        # If there is a non valid form that was submitted, redisplay the form with errors
        for submitted_form in forms_that_were_submitted:
            if not is_form_valid[submitted_form]:
                return render(request, self.template_name, context)

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
