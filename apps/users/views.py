from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView

from ayrabo.utils.mixins import PreSelectedTabMixin
from users.models import User


class UserDetailView(LoginRequiredMixin, PreSelectedTabMixin, DetailView):
    context_object_name = 'user'
    template_name = 'users/user_detail.html'
    queryset = User.objects.select_related('userprofile')
    INFO_TAB_KEY = 'information'
    SPORTS_TAB_KEY = 'sports'
    valid_tabs = [INFO_TAB_KEY, SPORTS_TAB_KEY]
    default_tab = INFO_TAB_KEY

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        user_profile = user.userprofile
        user_information = {
            'Gender': user_profile.get_gender_display(),
            'Age': user_profile.age,
            'Birthday': user_profile.birthday,
            'Height': user_profile.height,
            'Weight': user_profile.weight,
            'Timezone': user_profile.timezone
        }
        context.update({
            'info_tab_key': self.INFO_TAB_KEY,
            'sports_tab_key': self.SPORTS_TAB_KEY,
            'user_information': user_information,
            'sport_registration_data_by_sport': user.sport_registration_data_by_sport()
        })
        return context
