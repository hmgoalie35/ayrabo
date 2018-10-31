from django.core.validators import URLValidator
from django.db import models


DEFAULT_SCHEMES = ['http', 'https']


class WebsiteField(models.CharField):
    def __init__(self, *args, **kwargs):
        defaults = {
            'max_length': 255,
            'blank': True,
            'validators': [URLValidator(schemes=DEFAULT_SCHEMES)],
            'verbose_name': 'Website',
            'help_text': 'Make sure to include http:// or https://'
        }
        kwargs.update(defaults)
        super().__init__(*args, **kwargs)
