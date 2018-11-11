from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from easy_thumbnails.fields import ThumbnailerImageField

from ayrabo.utils import UploadTo
from ayrabo.utils.model_fields import WebsiteField
from common.models import TimestampedModel


class Team(TimestampedModel):
    """
    Represents a team. A division has many teams.
    """
    name = models.CharField(max_length=255, verbose_name='Name')
    slug = models.SlugField(max_length=255, verbose_name='Slug')
    logo = ThumbnailerImageField(verbose_name='Logo', upload_to=UploadTo('teams/logos/'), null=True, blank=True)
    website = WebsiteField()
    division = models.ForeignKey('divisions.Division', verbose_name='Division', on_delete=models.PROTECT,
                                 related_name='teams')
    locations = models.ManyToManyField('locations.Location', through='locations.TeamLocation', verbose_name='Locations',
                                       related_name='teams')
    organization = models.ForeignKey('organizations.Organization', verbose_name='Organization',
                                     on_delete=models.PROTECT, related_name='teams')

    def clean(self):
        self.slug = slugify(self.name)

        division = getattr(self, 'division', None)
        organization = getattr(self, 'organization', None)
        if division is not None and organization is not None:
            if division.league.sport_id != organization.sport_id:
                msg = 'Sports do not match {} and {}'.format(
                    division.league.sport.name, organization.sport.name)
                raise ValidationError({'organization': msg})

    class Meta:
        ordering = ['name', 'division']
        unique_together = (
            ('name', 'division'),
            ('slug', 'division')
        )

    def __str__(self):
        return self.name
