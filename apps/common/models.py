from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .managers import GenericChoiceManager


class GenericChoice(models.Model):
    """
    Represents dynamic choices for a model class or instance. This aims to simulate the choices kwarg for a
    CharField, but in a more dynamic manner.

    Aggregations (Sum, Avg, etc) work if an integer is stored in short/long value so no need to have sublasses of this
    model with different field types for short/long value.

    Ex: Multiple GenericChoices should be created for a given object, lets use the LIAHL league as an example. We
    can create exhibition and league choices which can be queried and displayed in a dropdown. The model that would
    normally have a CharField w/ choices should have a FK to `GenericChoice`.

    """
    TYPE_CHOICES = (
        ('game_type', 'Game Type'),
        ('game_point_value', 'Game Point Value'),
    )
    content_type = models.ForeignKey(ContentType, verbose_name='Content Type', on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField(verbose_name='Object Id')
    content_object = GenericForeignKey()
    short_value = models.CharField(verbose_name='Short Value', max_length=255,
                                   help_text='The value stored in the database')
    long_value = models.CharField(verbose_name='Long Value', max_length=255, help_text='The value shown to users')
    type = models.CharField(verbose_name='Type', max_length=255, choices=TYPE_CHOICES)

    objects = GenericChoiceManager()

    class Meta:
        unique_together = (('short_value', 'content_type', 'object_id'),)

    def __str__(self):
        return self.long_value
