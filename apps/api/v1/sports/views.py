from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from sports.exceptions import RoleDoesNotExistException, InvalidNumberOfRolesException
from sports.models import SportRegistration


class RemoveSportRegistrationRoleAPIView(APIView):
    def patch(self, request, *args, **kwargs):
        sr = get_object_or_404(SportRegistration, pk=kwargs.get('pk', None))
        role = kwargs.get('role', None)

        if request.user.id != sr.user_id:
            raise PermissionDenied()

        try:
            sr.remove_role(role)
        except RoleDoesNotExistException:
            return Response({'error': 'You are not currently registered as a {role}'.format(role=role)},
                            status.HTTP_400_BAD_REQUEST)
        except InvalidNumberOfRolesException:
            return Response(
                    {'error': 'You cannot remove the {role} role. You must be registered for at least one role.'.format(
                        role=role)},
                    status.HTTP_400_BAD_REQUEST)

        return Response({'detail': '{role} role successfully removed.'.format(role=role)})
