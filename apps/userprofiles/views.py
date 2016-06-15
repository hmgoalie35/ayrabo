from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView

from userprofiles.models import UserProfile
from .forms import CreateUserProfileForm, UpdateUserProfileForm


class CreateUserProfileView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = UserProfile
    template_name = 'userprofiles/create.html'
    success_message = 'Thank you for filling out your profile, you now have access to the entire site'
    success_url = reverse_lazy('home')
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
        return super(CreateUserProfileView, self).form_valid(form)


class UpdateUserProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UserProfile
    form_class = UpdateUserProfileForm
    template_name = 'userprofiles/update.html'
    success_url = reverse_lazy('update_userprofile')
    success_message = 'Your profile has been updated'
    context_object_name = 'userprofile'

    def get_object(self, queryset=None):
        return self.request.user.userprofile

    def form_valid(self, form):
        if form.has_changed():
            return super(UpdateUserProfileView, self).form_valid(form)
        else:
            return redirect(reverse('update_userprofile'))
