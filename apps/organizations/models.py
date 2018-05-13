from django.db import models
from django.utils.text import slugify

from common.models import TimestampedModel


class Organization(TimestampedModel):
    name = models.CharField(max_length=255, verbose_name='Name', unique=True)
    slug = models.SlugField(max_length=255, verbose_name='Slug')

    def clean(self):
        self.slug = slugify(self.name)

    def __str__(self):
        return self.name
