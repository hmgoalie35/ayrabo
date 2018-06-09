from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from ayrabo.utils.mixins import HasPermissionMixin, PreSelectedTabMixin
from organizations.models import Organization
from users.models import Permission


class OrganizationDetailView(LoginRequiredMixin, HasPermissionMixin, PreSelectedTabMixin, generic.DetailView):
    template_name = 'organizations/organization_detail.html'
    context_object_name = 'organization'
    model = Organization
    queryset = Organization.objects.prefetch_related('teams', 'teams__division', 'teams__division__league')
    valid_tabs = ['teams', 'organization_admins']
    default_tab = 'teams'

    def has_permission_func(self):
        user = self.request.user
        self.object = self.get_object()
        return user.has_object_permission('admin', self.object)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teams'] = self.object.teams.all()
        # Could alternatively setup a `GenericRelation` on `Organization`. Benefit of using a custom manager is that
        # we don't need to add the `GenericRelation` to every model class that could have a permission tied to it.
        context['organization_admins'] = [
            perm.user for perm in Permission.objects.get_permissions_for_object(name='admin', obj=self.object)
        ]
        context['support_email'] = settings.SUPPORT_EMAIL
        return context
