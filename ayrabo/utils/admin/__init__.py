from django.utils.html import format_html


def format_website_link(obj, attr='website'):
    url = getattr(obj, attr, None)
    if url:
        return format_html('<a target="_blank" rel="noopener noreferrer" href="{url}">{url}</a>', url=url)
    return None
