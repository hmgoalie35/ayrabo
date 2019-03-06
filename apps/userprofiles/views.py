from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from waffle import switch_is_active

from ayrabo.utils.mixins import PreSelectedTabMixin
from userprofiles.models import UserProfile
from .forms import UserProfileCreateUpdateForm


class UserProfileCreateView(LoginRequiredMixin, generic.CreateView):
    model = UserProfile
    template_name = 'userprofiles/userprofile_create.html'
    form_class = UserProfileCreateUpdateForm

    def get_success_url(self):
        if switch_is_active('sport_registrations'):
            return reverse('sports:register')
        return reverse('home')

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'userprofile'):
            return redirect(reverse('home'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UserProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, PreSelectedTabMixin, generic.UpdateView):
    model = UserProfile
    form_class = UserProfileCreateUpdateForm
    template_name = 'userprofiles/userprofile_update.html'
    success_url = reverse_lazy('account_home')
    success_message = 'Your account has been updated.'
    context_object_name = 'userprofile'
    valid_tabs = ['my_account', 'my_sports']
    default_tab = 'my_account'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sport_registration_data_by_sport'] = self.request.user.sport_registration_data_by_sport()
        return context

    def get_object(self, queryset=None):
        return self.request.user.userprofile

    def form_valid(self, form):
        if form.has_changed():
            return super().form_valid(form)
        else:
            return redirect(reverse('account_home'))
