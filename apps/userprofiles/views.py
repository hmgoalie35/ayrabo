from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import redirect, render
from django.views.generic import CreateView, UpdateView, View
from django.views.generic.base import ContextMixin

from coaches.forms import CoachForm
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
        context = super(FinishUserProfileView, self).get_context_data(**kwargs)
        user_roles = self.request.user.userprofile.roles
        # there is most likely a bug here when i start posting multiple forms to this view
        # self.request.POST will need to be parsed for the correct form data to instantiate the below forms with
        if 'Coach' in user_roles:
            context['coach_form'] = CoachForm(self.request.POST or None)
        if 'Player' in user_roles:
            context['player_form'] = None
        if 'Manager' in user_roles:
            context['manager_form'] = None
        if 'Referee' in user_roles:
            context['referee_form'] = None
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
        coach_form = context.get('coach_form')
        player_form = context.get('player_form')
        manager_form = context.get('manager_form')
        referee_form = context.get('referee_form')
        user = request.user
        if coach_form is not None:
            coach_form.instance.user = user
            if coach_form.is_valid():
                coach_form.save()
                user.userprofile.is_complete = True
                user.userprofile.save()
                messages.success(request, self.success_message)
                return redirect(reverse('home'))
        return render(request, self.template_name, context)


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
