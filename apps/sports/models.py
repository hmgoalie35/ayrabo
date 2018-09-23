from django.db import models
from django.utils.text import slugify

from common.models import TimestampedModel
from sports.managers import SportRegistrationManager


class Sport(TimestampedModel):
    """
    Represents a sport. This is the top of the hierarchy.
    """
    name = models.CharField(max_length=255, unique=True,
                            error_messages={'unique': 'Sport with this name already exists (case-insensitive)'})
    slug = models.SlugField(max_length=255, verbose_name='Slug', unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def clean(self):
        self.name = self.name.title()
        self.slug = slugify(self.name)

    def __str__(self):
        return self.name


class SportRegistration(TimestampedModel):
    ROLE_CHOICES = (
        ('player', 'Player'),
        ('coach', 'Coach'),
        ('referee', 'Referee'),
        ('manager', 'Manager'),
        ('scorekeeper', 'Scorekeeper'),
    )

    user = models.ForeignKey('users.User', verbose_name='User', on_delete=models.PROTECT,
                             related_name='sport_registrations')
    sport = models.ForeignKey(Sport, verbose_name='Sport', on_delete=models.PROTECT, related_name='sport_registrations')
    role = models.CharField(verbose_name='Role', max_length=64, choices=ROLE_CHOICES, db_index=True, null=True)

    roles_mask = models.SmallIntegerField(default=0, verbose_name='Roles Mask')
    # Signifies if each Coach, Referee, Manager, HockeyPlayer, etc. object has been created for all roles of this model
    is_complete = models.BooleanField(default=False, db_index=True, verbose_name='Is Registration Complete')

    objects = SportRegistrationManager()

    class Meta:
        ordering = ['user']
        unique_together = (
            ('user', 'sport', 'role'),
        )

    def __str__(self):
        return '{}: {} - {}'.format(self.user.email, self.get_role_display(), self.sport.name)
