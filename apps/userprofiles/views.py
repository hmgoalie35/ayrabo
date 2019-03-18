from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic
from waffle import switch_is_active

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
