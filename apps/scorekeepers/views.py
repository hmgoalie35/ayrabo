from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from ayrabo.utils.mixins import HasPermissionMixin
from scorekeepers.models import Scorekeeper
from sports.models import SportRegistration, Sport


class ScorekeepersCreateView(LoginRequiredMixin, HasPermissionMixin, generic.View):

    def has_permission_func(self):
        sport_registration = self._get_sport_registration()
        return self.request.user.id == sport_registration.user_id

    def _get_sport_registration(self):
        if hasattr(self, 'sport_registration'):
            return self.sport_registration
        self.sport_registration = get_object_or_404(
            SportRegistration.objects.select_related('user', 'sport'),
            pk=self.kwargs.get('pk', None)
        )
        return self.sport_registration

    def post(self, request, *args, **kwargs):
        self._get_sport_registration()
        user = request.user
        url = self.sport_registration.get_absolute_url()
        sport = self.sport_registration.sport
        # We want to include deactivated scorekeepers in these queries.
        scorekeepers = Scorekeeper.objects.filter(user=user)
        if scorekeepers.count() == Sport.objects.count():
            messages.info(request, 'You have already registered for all available sports. Please contact us to '
                                   'reactivate your scorekeeper registration.')
        elif scorekeepers.filter(sport=sport).exists():
            messages.info(request, 'Trying to reactivate your scorekeeper registration? Contact us.')
        else:
            self.sport_registration.set_roles(['Scorekeeper'], append=True)
            Scorekeeper.objects.create(user=user, sport=sport).full_clean()
            messages.success(request, 'You have been registered as a scorekeeper for {}.'.format(sport.name))
        return redirect(url)
