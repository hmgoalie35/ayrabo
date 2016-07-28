from django.db import models
from django.utils.text import slugify

from leagues.models import League


class Division(models.Model):
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
        return '{division} - {league}'.format(division=self.name, league=self.league.abbreviated_name)
