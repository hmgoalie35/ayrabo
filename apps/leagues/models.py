from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from sports.models import Sport


class League(models.Model):
    """
    Represents a league. A sport has many leagues and a league has many divisions.
    """
    full_name = models.CharField(max_length=255, verbose_name='Full Name',
                                 error_messages={'unique': 'League with this name already exists'})
    abbreviated_name = models.CharField(max_length=32, verbose_name='Abbreviated Name')
    slug = models.SlugField(verbose_name='Slug')
    sport = models.ForeignKey(Sport, verbose_name='Sport')
    created = models.DateTimeField(default=timezone.now, verbose_name='Created')

    class Meta:
        ordering = ['full_name']
        unique_together = (
            ('full_name', 'sport'),
            ('slug', 'sport')
        )

    def generate_abbreviation(self):
        """
        Generates an abbreviation based on the model's `full_name`. ex: National Hockey League --> NHL

        :return: Abbreviation for the model's `full_name`
        """
        # Takes the first letter of each word and concatenates them together.
        words = self.full_name.split(' ')
        return ''.join([word[:1].strip().upper() for word in words])

    def clean(self):
        abbreviated_name = self.generate_abbreviation()
        self.abbreviated_name = abbreviated_name
        self.slug = slugify(abbreviated_name)

    def __str__(self):
        return self.full_name
