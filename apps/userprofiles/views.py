from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from userprofiles.models import UserProfile
from django.shortcuts import redirect
from django.core.urlresolvers import reverse, reverse_lazy
from .forms import UserProfileForm


class CreateUserProfileView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = UserProfile
    template_name = 'userprofiles/create.html'
    success_message = 'Thank you for filling out your profile, you now have access to the entire site'
    success_url = reverse_lazy('home')
    form_class = UserProfileForm

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
