from urllib.parse import urlencode, urljoin

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse


def url_with_query_string(url, **kwargs):
    return f'{url}?{urlencode(kwargs)}'


def get_absolute_url(url_or_url_name, *args, **kwargs):
    protocol = 'http' if settings.DEBUG else 'https'
    site = get_current_site(request=None)
    url = reverse(url_or_url_name, args=args, kwargs=kwargs)
    return urljoin(f'{protocol}://{site.domain}', url)
