from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from common.models import TimestampedModel


class User(AbstractUser):
    pass


class Permission(TimestampedModel):
    PERMISSION_CHOICES = (
        ('admin', 'Admin'),
    )
    user = models.ForeignKey('users.User', verbose_name='User', related_name='permissions')
    name = models.CharField(max_length=255, choices=PERMISSION_CHOICES, verbose_name='Name')
    content_type = models.ForeignKey(ContentType, verbose_name='Content Type', related_name='permissions')
    object_id = models.PositiveIntegerField(verbose_name='Object ID')
    content_object = GenericForeignKey()

    class Meta:
        unique_together = (
            ('user', 'name', 'content_type', 'object_id'),
        )

    def __str__(self):
        return '<{}> {} {}'.format(self.user.email, self.content_type.name, self.name)
