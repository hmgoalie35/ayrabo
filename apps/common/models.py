from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .managers import GenericModelChoiceManager


class GenericModelChoice(models.Model):
    """
    Used to represent dynamic choices for a model or model instance. This aims to simulate the choices kwarg for a
    CharField, but in a more dynamic manner.
    Ex: Multiple GenericModelChoices should be created for a given object, lets use the LIAHL league as an example. We
    can create exhibition and league choices which can be queried and displayed in a dropdown. The model that would
    normally have a CharField w/ choices should have a FK to `GenericModelChoice`.
    """
    content_type = models.ForeignKey(ContentType, verbose_name='Content Type', on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField(verbose_name='Object Id')
    content_object = GenericForeignKey()
    short_name = models.CharField(verbose_name='Short Name', max_length=255,
                                  help_text='The value stored in the database')
    long_name = models.CharField(verbose_name='Long Name', max_length=255, help_text='The value shown to users')

    objects = GenericModelChoiceManager()

    class Meta:
        unique_together = (('short_name', 'content_type', 'object_id'),)

    def __str__(self):
        return self.long_name
