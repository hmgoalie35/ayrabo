from itertools import groupby

from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from coaches.models import Coach
from common.models import TimestampedModel
from managers.models import Manager
from organizations.models import Organization
from referees.models import Referee
from scorekeepers.models import Scorekeeper
from users.managers import PermissionManager


class User(AbstractUser):
    def has_object_permission(self, name, obj):
        content_type = ContentType.objects.get_for_model(obj)
        return self.permissions.filter(name=name, content_type=content_type, object_id=obj.id).exists()

    def get_sport_registrations(self):
        """
        Fetches sport registrations for the user, making sure to omit any legacy sport registrations.
        NOTE: Legacy sport registrations used roles_mask so role will be None

        :return: Sport registrations for the user
        """
        return self.sport_registrations.exclude(role=None).order_by('sport', 'role').select_related('sport')

    def sport_registration_data_by_sport(self):
        """
        Groups sport registrations by sport, additionally computing extra meta data for the sport and sport
        registrations. The registrations and role objects are computed for each sport.

        Ex:
        {
            <Sport Ice Hockey>: {
                'registrations': [...],
                'roles': {
                    'coach': [...]
                }
            },
            <Sport Baseball>: {
                'registrations': [...],
                'roles': {
                    'manager': [...],
                    'player': [],
                    'referee': [...]
                }
            }
        }

        :return: Dict where keys are sports the user is registered for and values are additional meta data regarding
        the user's registration for that sport.
        """
        result = {}
        for sport, registrations in groupby(self.get_sport_registrations(), key=lambda obj: obj.sport):
            registrations_as_list = list(registrations)
            result[sport] = {
                'registrations': registrations_as_list,
                'roles': self.get_roles(sport, registrations_as_list)
            }
        return result

    def get_roles(self, sport, sport_registrations):
        """
        Computes all roles for the current user (and sport) and the role objects for each role.

        :param sport: The sport to get role objects for
        :param sport_registrations: Sport registrations for the user.
        :return: dict where the keys are the roles the user is registered for and the values are objects for that role
        """
        result = {}
        roles = [sr.role for sr in sport_registrations]
        content_type = ContentType.objects.get_for_model(Organization)
        permissions = self.permissions.filter(name='admin', content_type=content_type)
        organizations = [perm.content_object for perm in permissions]
        organizations_for_sport = [o for o in organizations if o.sport_id == sport.id]
        if len(organizations_for_sport) > 0:
            roles.append('organization')
        sorted_roles = sorted(roles)
        for role in sorted_roles:
            objects = self.get_objects_for_role(sport, role, organizations_for_sport)
            result[role] = objects
        return result

    def get_objects_for_role(self, sport, role, qs=None):
        if role == 'player':
            return self.get_players(sport)
        if role == 'coach':
            return self.get_coaches(sport)
        if role == 'referee':
            return self.get_referees(sport)
        if role == 'manager':
            return self.get_managers(sport)
        if role == 'scorekeeper':
            return self.get_scorekeepers(sport)
        if role == 'organization':
            return self.get_organizations(sport, qs)
        return None

    def get_players(self, sport):
        """
        Fetches players for the user, if the sport has not been configured an empty list is returned.
        NOTE: Be careful calling queryset functions on the return value of this function. If the sport has not been
        configured, a list will be returned which does not support queryset functions.

        :param sport: Sport to fetch players for
        :return: Empty list if the sport has not been configured, otherwise a queryset of player objects for the user
        and sport.
        """
        # Prevents circular import error
        from ayrabo.utils.mappings import SPORT_PLAYER_MODEL_MAPPINGS

        player_model_cls = SPORT_PLAYER_MODEL_MAPPINGS.get(sport.name)
        if player_model_cls is None:
            return []
        return player_model_cls.objects.active().filter(user=self, sport=sport).select_related('team__division',
                                                                                               'sport')

    def get_coaches(self, sport):
        return Coach.objects.active().filter(user=self, team__division__league__sport=sport).select_related(
            'team__division__league__sport')

    def get_referees(self, sport):
        return Referee.objects.active().filter(user=self, league__sport=sport).select_related('league__sport')

    def get_managers(self, sport):
        return Manager.objects.active().filter(user=self, team__division__league__sport=sport).select_related(
            'team__division__league__sport')

    def get_scorekeepers(self, sport):
        return Scorekeeper.objects.active().filter(user=self, sport=sport).select_related('sport')

    def get_organizations(self, sport, qs):
        return qs


class Permission(TimestampedModel):
    PERMISSION_CHOICES = (
        ('admin', 'Admin'),
    )
    user = models.ForeignKey('users.User', verbose_name='User', related_name='permissions')
    name = models.CharField(max_length=255, choices=PERMISSION_CHOICES, verbose_name='Name', db_index=True)
    content_type = models.ForeignKey(ContentType, verbose_name='Content Type', related_name='permissions')
    object_id = models.PositiveIntegerField(verbose_name='Object ID')
    content_object = GenericForeignKey()

    objects = PermissionManager()

    class Meta:
        unique_together = (
            ('user', 'name', 'content_type', 'object_id'),
        )

    def __str__(self):
        return '<{}> {} {}'.format(self.user.email, self.content_type.name, self.name)
