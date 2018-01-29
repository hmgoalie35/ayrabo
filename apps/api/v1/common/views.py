from django.shortcuts import get_object_or_404
from rest_framework import views, status
from rest_framework.response import Response

from api import permissions
from sports.exceptions import InvalidNumberOfRolesException
from sports.models import SportRegistration


class BaseDeactivateApiView(views.APIView):
    permission_classes = (permissions.IsObjectOwner,)

    def get_url_lookup_kwarg(self):
        raise NotImplementedError()

    def get_model(self, sport_name):
        raise NotImplementedError()

    def get_role(self):
        raise NotImplementedError()

    def _get_sport_registration(self):
        return get_object_or_404(SportRegistration.objects.select_related('sport'), pk=self.kwargs.get('pk', None))

    def _get_object(self, sport_name):
        lookup_kwarg = self.get_url_lookup_kwarg()
        model_cls = self.get_model(sport_name)
        return get_object_or_404(model_cls, pk=self.kwargs.get(lookup_kwarg, None))

    def patch(self, request, *args, **kwargs):
        sport_registration = self._get_sport_registration()
        self.check_object_permissions(request, sport_registration)
        sport_name = sport_registration.sport.name
        obj = self._get_object(sport_name)
        self.check_object_permissions(request, obj)

        model_cls = self.get_model(sport_name)

        user = request.user
        role = self.get_role()

        obj.is_active = False
        obj.save()

        filter_kwargs = {'user': user}
        if role == 'referee':
            filter_kwargs['league__sport'] = sport_registration.sport
        elif role == 'scorekeeper':
            filter_kwargs['sport'] = sport_registration.sport
        else:
            filter_kwargs['team__division__league__sport'] = sport_registration.sport

        active_objs = model_cls.objects.active().filter(**filter_kwargs)
        if not active_objs.exists():
            try:
                sport_registration.remove_role(role)
            except InvalidNumberOfRolesException:
                msg = 'You cannot remove the {} role. You must be registered for at least one role.'.format(role)
                obj.is_active = True
                obj.save()
                return Response({'error': msg}, status.HTTP_400_BAD_REQUEST)
        return Response()
