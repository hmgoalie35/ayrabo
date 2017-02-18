from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from escoresheet.utils.mixins import UserHasRolesMixin
from managers.models import Manager


class ManagerHomeView(LoginRequiredMixin, UserHasRolesMixin, generic.TemplateView):
    template_name = 'managers/manager_home.html'
    roles_to_check = ['Manager']

    def get_context_data(self, **kwargs):
        context = super(ManagerHomeView, self).get_context_data(**kwargs)
        # A user has many manager objects, with each manager object being tied to a team
        manager_objects = Manager.objects.filter(user=self.request.user).select_related('team',
                                                                                        'team__division__league__sport')
        context['teams'] = [manager.team for manager in manager_objects]
        return context
