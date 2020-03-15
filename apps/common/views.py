from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.views import generic


class HealthCheckView(generic.View):
    def get(self, request, *args, **kwargs):
        # This call gets cached
        site = get_current_site(request)
        # Actually hit the database to check for connectivity
        ContentType.objects.first()
        return HttpResponse('{} is up'.format(site.domain))
