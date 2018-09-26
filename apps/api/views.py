from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.generics import get_object_or_404


class RevokeAuthTokenView(generics.DestroyAPIView):
    """
    Deletes the API token for the user making the request.
    """
    queryset = Token.objects.all()

    def get_object(self):
        token = get_object_or_404(Token, user=self.request.user)
        # This view doesn't have any permission classes checking object permissions, but for consistency let's have this
        # check.
        self.check_object_permissions(self.request, token)
        return token
