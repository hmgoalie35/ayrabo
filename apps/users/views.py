from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import generic
from django.views.generic.base import ContextMixin

from ayrabo.utils.mixins import PreSelectedTabMixin
from userprofiles.forms import UserProfileCreateUpdateForm
from userprofiles.models import UserProfile
from users.forms import UserUpdateForm
from users.models import User
from users.tabs import INFO_TAB_KEY, SPORTS_TAB_KEY
from users.utils import get_user_detail_view_context


class UserDetailView(LoginRequiredMixin, PreSelectedTabMixin, generic.DetailView):
    """
    Need to make sure we specify `context_object_name`, and that it's not set to `user`. Auth middleware sets `user`
    so overwriting that is going to cause problems, one being the email shown in the account navbar dropdown.
    https://github.com/django/django/blob/master/django/views/generic/detail.py#L87 causes problems if no
    `context_object_name` is specified.
    """
    context_object_name = 'user_obj'
    template_name = 'users/user_detail.html'
    queryset = User.objects.select_related('userprofile')
    valid_tabs = [INFO_TAB_KEY, SPORTS_TAB_KEY]
    default_tab = INFO_TAB_KEY

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        try:
            user_profile = user.userprofile
            user_information = {
                'Gender': user_profile.get_gender_display(),
                'Age': user_profile.age,
                'Birthday': user_profile.birthday,
                'Height': user_profile.height,
                'Weight': user_profile.weight,
                'Timezone': user_profile.timezone
            }
        except UserProfile.DoesNotExist:
            user_information = {}
        context.update({
            'user_information': user_information,
            'sport_registration_data_by_sport': user.sport_registration_data_by_sport()
        })
        # This detail view is already setting `user_obj` for us, so this util function doesn't need to.
        context.update(get_user_detail_view_context(self.request, user, include_user_obj=False))
        return context


class UserUpdateView(LoginRequiredMixin, ContextMixin, generic.View):
    template_name = 'users/user_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        data = self.request.POST or None
        user_form = UserUpdateForm(instance=user, data=data)
        user_profile_form = UserProfileCreateUpdateForm(instance=user.userprofile, data=data)
        context.update({
            'user_form': user_form,
            'user_profile_form': user_profile_form,
            'active_tab': INFO_TAB_KEY
        })
        context.update(get_user_detail_view_context(self.request, user, include_user_obj=True))
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        user_form = context.get('user_form')
        user_profile_form = context.get('user_profile_form')
        if user_form.is_valid() and user_profile_form.is_valid():
            user_form_changed = user_form.has_changed()
            user_profile_form_changed = user_profile_form.has_changed()
            if user_form_changed:
                user_form.save()
            if user_profile_form_changed:
                user_profile_form.save()
            if user_form_changed or user_profile_form_changed:
                messages.success(request, 'Your account information has been updated.')
            return redirect('users:detail', pk=request.user.pk)
        return render(request, self.template_name, context)
