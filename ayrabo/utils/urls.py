from urllib.parse import urlencode


def url_with_query_string(url, **kwargs):
    return '{}?{}'.format(url, urlencode(kwargs))
