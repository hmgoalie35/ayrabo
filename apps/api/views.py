from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse as drf_reverse
from rest_framework.settings import api_settings
from rest_framework.views import APIView


class APIHomeView(APIView):
    """
    The home page for the API. It contains documentation on how to use the API as well as links to specific api versions.
    The links to the api versions contain all endpoints for that version.

    The reason this view inherits from APIView and not django's TemplateView is so the browsable api provided by drf
    displays "Api Home" as a breadcrumb.
    """
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        api_versions = {}
        for api_version in api_settings.ALLOWED_VERSIONS:
            api_versions[api_version] = drf_reverse('{version}:{version}_home'.format(version=api_version))

        context = {
            'api_versions': api_versions,
            'default_api_version': api_settings.DEFAULT_VERSION,
            'obtain_api_token_path': drf_reverse('obtain_api_token', request=request),
            'generic_endpoints': [drf_reverse('obtain_api_token', request=request),
                                  drf_reverse('revoke_api_token', request=request)]
        }

        return Response(context, template_name='api/api_home.html')


class RevokeAuthTokenView(generics.DestroyAPIView):
    """
    Deletes the API token for the user making the request.
    """
    queryset = Token.objects.all()

    def get_object(self):
        token = get_object_or_404(Token, user=self.request.user)
        return token
