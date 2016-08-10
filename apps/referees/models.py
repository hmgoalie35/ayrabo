from django.contrib.auth.models import User
from django.core.validators import ValidationError
from django.db import models

from leagues.models import League
from sports.models import SportRegistration


class Referee(models.Model):
    user = models.ForeignKey(User)
    league = models.ForeignKey(League)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Created')

    class Meta:
        unique_together = (('user', 'league'),)

    def clean(self):
        # hasattr is needed for when the admin panel is used, an object w/o those fields may be created by accident
        if hasattr(self, 'user') and hasattr(self, 'league'):
            sport = self.league.sport
            qs = SportRegistration.objects.filter(user=self.user, sport=sport)
            if qs.exists() and not qs.first().has_role('Referee'):
                raise ValidationError(
                        '{user} - {sport} might not have a sportregistration object or the sportregistration object does not have the referee role assigned'.format(
                                user=self.user.email, sport=sport.name))

    def __str__(self):
        return 'Referee {full_name}'.format(full_name=self.user.get_full_name())
