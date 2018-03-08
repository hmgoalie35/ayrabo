from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from rest_framework.authtoken.models import Token

from sports.models import SportRegistration
from userprofiles.models import UserProfile
from .forms import UserProfileCreateForm, UserProfileUpdateForm


class UserProfileCreateView(LoginRequiredMixin, generic.CreateView):
    model = UserProfile
    template_name = 'userprofiles/userprofile_create.html'
    success_url = reverse_lazy('sportregistrations:create')
    form_class = UserProfileCreateForm

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'userprofile'):
            return redirect(reverse('home'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(UserProfileCreateView, self).form_valid(form)


class UserProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = UserProfile
    form_class = UserProfileUpdateForm
    template_name = 'userprofiles/userprofile_update.html'
    success_url = reverse_lazy('account_home')
    success_message = 'Your account has been updated.'
    context_object_name = 'userprofile'

    def get_context_data(self, **kwargs):
        context = super(UserProfileUpdateView, self).get_context_data(**kwargs)
        sport_registrations = SportRegistration.objects.filter(user=self.request.user).select_related('sport', 'user')
        data = {}
        for sport_registration in sport_registrations:
            data[sport_registration] = {'sport': sport_registration.sport, 'roles': sport_registration.roles,
                                        'related_objects': sport_registration.get_related_role_objects()}
        context['data'] = data
        api_tokens = Token.objects.filter(user=self.request.user)
        context['api_token'] = api_tokens.first() if api_tokens.exists() else None

        tab = self.request.GET.get('tab', None)
        # Handle people manually putting in query strings.
        context['tab'] = tab if tab in ['my-account', 'my-sports'] else None
        return context

    def get_object(self, queryset=None):
        return self.request.user.userprofile

    def form_valid(self, form):
        if form.has_changed():
            return super(UserProfileUpdateView, self).form_valid(form)
        else:
            return redirect(reverse('account_home'))
