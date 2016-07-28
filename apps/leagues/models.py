from django.db import models
from django.utils.text import slugify

from sports.models import Sport


class League(models.Model):
    full_name = models.CharField(max_length=255, verbose_name='Full Name',
                                 error_messages={'unique': 'League with this name already exists'})
    abbreviated_name = models.CharField(max_length=32, verbose_name='Abbreviated Name')
    slug = models.SlugField(verbose_name='Slug')
    sport = models.ForeignKey(Sport, verbose_name='Sport')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Created')

    class Meta:
        ordering = ['full_name']
        unique_together = (
            ('full_name', 'sport'),
            ('slug', 'sport')
        )

    def clean(self):
        # Takes the first letter of each word and concatenates them together. ex: National Hockey League --> NHL
        words = self.full_name.split(' ')
        self.abbreviated_name = ''.join([word[:1].strip().upper() for word in words])

        self.slug = slugify(self.abbreviated_name)

    def __str__(self):
        return self.full_name
