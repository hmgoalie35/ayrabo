from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.views import generic
from rest_framework.authtoken.models import Token

from sports.models import SportRegistration
from userprofiles.models import UserProfile
from .forms import CreateUserProfileForm, UpdateUserProfileForm


def check_account_and_sport_registration_completed(request):
    """
    This helper function performs the same thing as the middleware, but because the middleware lets the whitelisted
    urls through, we need to do the check again in the actual view.

    :param request: The request object passed to the view
    :return: redirect_url: The url to redirect to, redirect_needed: If the redirect needs to happen
    """
    # These checks are needed because the middleware allows through any request from the whitelisted urls
    up = UserProfile.objects.filter(user=request.user)
    sport_registrations = SportRegistration.objects.filter(user=request.user)
    incomplete_sport_registrations = sport_registrations.filter(is_complete=False)
    redirect_url = None
    request.session['is_user_currently_registering'] = False
    if not up.exists():
        redirect_url = reverse('profile:create')
        request.session['is_user_currently_registering'] = True
    elif not sport_registrations.exists():
        request.session['is_user_currently_registering'] = True
        redirect_url = reverse('sport:create_sport_registration')
    elif incomplete_sport_registrations.exists():
        request.session['is_user_currently_registering'] = True
        redirect_url = reverse('sport:finish_sport_registration')
    # The latter part of this statement prevents redirect loops
    redirect_needed = redirect_url is not None and request.path != redirect_url
    return redirect_url, redirect_needed


class CreateUserProfileView(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    model = UserProfile
    template_name = 'userprofiles/userprofile_create.html'
    success_url = reverse_lazy('sport:create_sport_registration')
    success_message = 'Your profile has been created.'
    form_class = CreateUserProfileForm

    def get(self, request, *args, **kwargs):
        redirect_url, redirect_needed = check_account_and_sport_registration_completed(request)
        if redirect_needed:
            return redirect(redirect_url)
        return super(CreateUserProfileView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        redirect_url, redirect_needed = check_account_and_sport_registration_completed(request)
        if redirect_needed:
            return redirect(redirect_url)
        return super(CreateUserProfileView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(CreateUserProfileView, self).form_valid(form)


class UpdateUserProfileView(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = UserProfile
    form_class = UpdateUserProfileForm
    template_name = 'userprofiles/userprofile_update.html'
    success_url = reverse_lazy('account_home')
    success_message = 'Your profile has been updated'
    context_object_name = 'userprofile'

    def get_context_data(self, **kwargs):
        context = super(UpdateUserProfileView, self).get_context_data(**kwargs)
        sport_registrations = SportRegistration.objects.filter(user=self.request.user).select_related('sport')
        data = {}
        for sport_registration in sport_registrations:
            data[sport_registration] = {'sport': sport_registration.sport, 'roles': sport_registration.roles,
                                        'related_objects': sport_registration.get_related_role_objects()}
        context['data'] = data
        api_tokens = Token.objects.filter(user=self.request.user)
        context['api_token'] = api_tokens.first() if api_tokens.exists() else None
        return context

    def get_object(self, queryset=None):
        return self.request.user.userprofile

    def form_valid(self, form):
        if form.has_changed():
            return super(UpdateUserProfileView, self).form_valid(form)
        else:
            return redirect(reverse('account_home'))
