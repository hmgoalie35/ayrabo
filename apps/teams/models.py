from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from easy_thumbnails.fields import ThumbnailerImageField

from ayrabo.utils import UploadTo
from ayrabo.utils.model_fields import WebsiteField
from common.models import TimestampedModel
from divisions.models import Division


class Team(TimestampedModel):
    """
    Represents a team. A division has many teams.
    """
    name = models.CharField(max_length=255, verbose_name='Name')
    slug = models.SlugField(max_length=255, verbose_name='Slug')
    logo = ThumbnailerImageField(verbose_name='Logo', upload_to=UploadTo('teams/logos/'), null=True)
    website = WebsiteField()
    division = models.ForeignKey(Division)
    locations = models.ManyToManyField('locations.Location', through='locations.TeamLocation', verbose_name='Locations',
                                       related_name='teams')
    organization = models.ForeignKey('organizations.Organization', verbose_name='Organization',
                                     on_delete=models.PROTECT, related_name='teams')

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
