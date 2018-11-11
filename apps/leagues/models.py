from django.db import models
from django.utils.text import slugify
from easy_thumbnails.fields import ThumbnailerImageField

from ayrabo.utils import UploadTo
from ayrabo.utils.model_fields import WebsiteField
from common.models import TimestampedModel
from sports.models import Sport


class League(TimestampedModel):
    """
    Represents a league. A sport has many leagues and a league has many divisions.
    """
    name = models.CharField(max_length=255, verbose_name='Name',
                            error_messages={'unique': 'League with this name already exists'})
    abbreviated_name = models.CharField(max_length=32, verbose_name='Abbreviated Name')
    slug = models.SlugField(max_length=255, verbose_name='Slug')
    sport = models.ForeignKey(Sport, verbose_name='Sport')
    logo = ThumbnailerImageField(verbose_name='Logo', upload_to=UploadTo('leagues/logos/'), null=True, blank=True)
    website = WebsiteField()

    class Meta:
        ordering = ['name']
        unique_together = (
            ('name', 'sport'),
            ('slug', 'sport')
        )

    def generate_abbreviation(self):
        """
        Generates an abbreviation based on the model's `name`. ex: National Hockey League --> NHL

        :return: Abbreviation for the model's `name`
        """
        # Takes the first letter of each word and concatenates them together.
        words = self.name.split(' ')
        return ''.join([word[:1].strip().upper() for word in words])

    def clean(self):
        abbreviated_name = self.generate_abbreviation()
        self.abbreviated_name = abbreviated_name
        self.slug = slugify(abbreviated_name)

    def __str__(self):
        return self.name
