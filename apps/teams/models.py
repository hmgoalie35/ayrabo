from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from divisions.models import Division
from ayrabo.utils.model_fields import WebsiteField


class Team(models.Model):
    """
    Represents a team. A division has many teams.
    """
    name = models.CharField(max_length=255, verbose_name='Name')
    slug = models.SlugField(verbose_name='Slug')
    website = WebsiteField()
    division = models.ForeignKey(Division)
    locations = models.ManyToManyField('locations.Location', through='locations.TeamLocation', verbose_name='Locations',
                                       related_name='teams')
    created = models.DateTimeField(default=timezone.now, verbose_name='Created')

    """
    The fields below are not really necessary to store in this model for the MVP, a link to the team's website would
    provide all of this info and more. However, in the future it might be useful to add fields like below to this model
    or even create a TeamInfo model

    president - CharField
    governor - CharField, should be optional?
    office_address - CharField
    office_phone - CharField
    """

    def clean(self):
        self.slug = slugify(self.name)

    class Meta:
        ordering = ['name', 'division']
        unique_together = (
            ('name', 'division'),
            ('slug', 'division')
        )

    def __str__(self):
        return self.name
