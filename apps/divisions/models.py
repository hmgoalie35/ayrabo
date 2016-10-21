from django.db import models
from django.utils.text import slugify

from leagues.models import League


class Division(models.Model):
    """
    Represents a division that belongs to a league. Teams belong to divisions. A league has many divisions and a division has many teams.
    """
    name = models.CharField(max_length=255, verbose_name='Name')
    slug = models.SlugField(verbose_name='Slug')
    league = models.ForeignKey(League)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Created')

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
