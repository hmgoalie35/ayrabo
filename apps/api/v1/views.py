from rest_framework.response import Response
from rest_framework.views import APIView


class V1View(APIView):
    """
    V1 of the API
    """

    def get(self, request, *args, **kwargs):
        context = {
            'info': 'This will eventually have all endpoints for v1 listed out...'
        }

        return Response(context)
