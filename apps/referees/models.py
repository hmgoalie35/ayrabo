from django.contrib.auth.models import User
from django.core.validators import ValidationError
from django.db import models
from django.utils import timezone

from common import managers
from leagues.models import League
from sports.models import SportRegistration


class Referee(models.Model):
    """
    Represents a referee in the system. A user can have many Referee objects related to them provided each referee
    object is for a different league.
    TLDR; A user can be a referee for multiple leagues and a new referee object is created for each league.
    """
    user = models.ForeignKey(User, related_name='referees')
    league = models.ForeignKey(League)
    created = models.DateTimeField(default=timezone.now, verbose_name='Created')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')

    objects = managers.ActiveManager()

    class Meta:
        unique_together = (('user', 'league'),)

    def clean(self):
        # hasattr is needed for when the admin panel is used, an object w/o those fields may be created by accident
        if hasattr(self, 'user') and hasattr(self, 'league'):
            sport = self.league.sport
            qs = SportRegistration.objects.filter(user=self.user, sport=sport)
            if qs.exists() and not qs.first().has_role('Referee'):
                raise ValidationError(
                        '{user} - {sport} might not have a sportregistration object or the sportregistration '
                        'object does not have the referee role assigned'.format(
                                user=self.user.email, sport=sport.name)
                )

    def __str__(self):
        return 'Referee {full_name}'.format(full_name=self.user.get_full_name())
