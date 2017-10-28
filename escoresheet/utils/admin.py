from django.utils.html import format_html


def format_website_link(obj, attr='website'):
    return format_html('<a target="_blank" rel="noopener noreferrer" href="{url}">{url}</a>',
                       url=getattr(obj, attr)) if getattr(obj, attr) else None
