from django.db import models
from django.utils.text import slugify

from common.models import TimestampedModel


class Division(TimestampedModel):
    """
    Represents a division that belongs to a league.
    Teams belong to divisions.
    A league has many divisions and a division has many teams.
    """
    name = models.CharField(max_length=255, verbose_name='Name')
    slug = models.SlugField(max_length=255, verbose_name='Slug')
    league = models.ForeignKey('leagues.League', verbose_name='League', on_delete=models.PROTECT,
                               related_name='divisions')

    def clean(self):
        self.slug = slugify(self.name)

    class Meta:
        ordering = ['name']
        unique_together = (
            ('name', 'league'),
            ('slug', 'league')
        )

    def __str__(self):
        return self.name
