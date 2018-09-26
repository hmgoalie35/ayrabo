from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated


class RevokeAuthTokenView(generics.DestroyAPIView):
    """
    Deletes the API token for the user making the request.
    """
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Token.objects.filter(user=self.request.user).select_related('user')

    def get_object(self):
        qs = self.get_queryset()
        token = get_object_or_404(qs, user=self.request.user)
        self.check_object_permissions(self.request, token)
        return token
