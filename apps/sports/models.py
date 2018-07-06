from django.db import models
from django.utils.text import slugify

import coaches as coaches_app
import managers as managers_app
import players as players_app
import referees as referees_app
import scorekeepers as scorekeepers_app
from common.models import TimestampedModel
from .exceptions import InvalidNumberOfRolesException, RoleDoesNotExistException


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
    """
    Model used to store what roles a user has for a sport. A user chooses to register for a sport and has the option to
    choose what role(s) they want for a specific sport

    i.e. user John might want to be a Player and Referee for Ice Hockey, but only wants to be a Coach for Soccer. There
    would b 2 SportRegistration objects, both tied to John but one is for Ice Hockey with roles_mask corresponding to
    Player and Referee and another tied to sport Soccer with a roles_mask corresponding to Coach
    """

    ROLES = ['Player', 'Coach', 'Referee', 'Manager', 'Scorekeeper']

    user = models.ForeignKey('users.User')
    sport = models.ForeignKey(Sport)
    roles_mask = models.SmallIntegerField(default=0, verbose_name='Roles Mask')
    # Signifies if each Coach, Referee, Manager, HockeyPlayer, etc. object has been created for all roles of this model
    is_complete = models.BooleanField(default=False, db_index=True, verbose_name='Is Registration Complete')

    class Meta:
        ordering = ['user']
        unique_together = (
            ('user', 'sport'),
        )

    def set_roles(self, roles, append=False):
        """
        Given a list of roles (taken from ROLES) creates a mask (int) that represents the roles currently valid for this
        user for a given sport

        :param append: Set to True to indicate you want to append roles to any existent roles, set to False to overwrite
            any existing roles with roles
        :param roles: The role(s) to add
        """

        assert isinstance(roles, list)

        # & performs an intersection and will omit any roles that are misspelled or DNE
        valid_roles = set(roles) & set(self.ROLES)
        accumulator = 0
        for role in valid_roles:
            accumulator += 2 ** self.ROLES.index(role)
        if append:
            self.roles_mask += accumulator
        else:
            self.roles_mask = accumulator
        self.save()

    def remove_role(self, role):
        """
        Given a role attempts to remove that role.

        :raise RoleDoesNotExistException: if the sport registration does not have the specified role.
        :raise InvalidNumberOfRolesException: if removing the role would result in the sport registration
            having no roles.
        :param role: The role to remove.
        """
        if not self.has_role(role):
            raise RoleDoesNotExistException()

        new_roles = list(set(self.roles) - {role.title()})

        if new_roles:
            self.set_roles(new_roles)
        else:
            raise InvalidNumberOfRolesException()

    @property
    def roles(self):
        """
        Converts the role mask (int) to the actual roles (strings)

        :return: A list containing all of the roles associated with the user
        """
        return [role for role in self.ROLES if (self.roles_mask & 2 ** self.ROLES.index(role)) != 0]

    def has_role(self, role):
        """
        Checks to see if the current user has the specified role for the appropriate sport

        :param role: The role to check for (case insensitive)
        :return: True if the user has the current role, False otherwise
        """
        return role.title() in self.roles or role in self.roles

    def _get_objects(self, model_cls, filter_kwargs, selected_related=[]):
        return model_cls.objects.active().filter(**filter_kwargs).select_related(*selected_related)

    def get_related_role_objects(self):
        """
        This function iterates through all of the roles for the sport registration and retrieves the appropriate
        object that goes with the role. i.e. Roles Coach and Manager are set, so this function will fetch the Coach
        and Manager objects for the given user and sport

        :return: A dictionary where the keys are the role (Player, Coach, etc.) and the value is the associated object
        """

        SPORT_MODEL_MAPPINGS = {
            'Ice Hockey': players_app.models.HockeyPlayer,
            'Baseball': players_app.models.BaseballPlayer,
            'Basketball': players_app.models.BasketballPlayer,
        }

        obj_role_mappings = {}
        roles = self.roles
        user = self.user_id
        sport = self.sport
        sport_name = sport.name

        for role in roles:
            if role == 'Player':
                players = None
                model_cls = SPORT_MODEL_MAPPINGS.get(sport_name)
                if model_cls is not None:
                    players = self._get_objects(model_cls, {'user': user, 'sport': sport}, ['team', 'team__division'])
                obj_role_mappings['Player'] = players if players and players.exists() else None
            elif role == 'Coach':
                coaches = self._get_objects(coaches_app.models.Coach,
                                            {'user': user, 'team__division__league__sport': sport},
                                            ['team', 'team__division'])
                obj_role_mappings['Coach'] = coaches if coaches.exists() else None
            elif role == 'Manager':
                managers = self._get_objects(managers_app.models.Manager,
                                             {'user': user, 'team__division__league__sport': sport},
                                             ['team', 'team__division'])
                obj_role_mappings['Manager'] = managers if managers.exists() else None
            elif role == 'Referee':
                referees = self._get_objects(referees_app.models.Referee, {'user': user, 'league__sport': sport},
                                             ['league'])
                obj_role_mappings['Referee'] = referees if referees.exists() else None
            elif role == 'Scorekeeper':
                scorekeepers = self._get_objects(scorekeepers_app.models.Scorekeeper, {'user': user, 'sport': sport})
                obj_role_mappings['Scorekeeper'] = scorekeepers if scorekeepers.exists() else None
        return obj_role_mappings

    # TODO Figure out a better way to do this, it seems really inefficient to run get_related_objects on every request.
    # Add boolean fields to sport reg model for is_player_complete, etc. Or store completed roles in db array field
    def get_next_namespace_for_registration(self):
        """
        Figures out what namespace (which can be mapped to a role) should be registered for next.

        :return: The namespace corresponding to the first role that doesn't have related objects, otherwise
         None if all roles had related objects created.
        """
        related_objects = self.get_related_role_objects()
        if self.has_role('Player') and related_objects.get('Player') is None:
            namespace = 'players'
        elif self.has_role('Coach') and related_objects.get('Coach') is None:
            namespace = 'coaches'
        elif self.has_role('Referee') and related_objects.get('Referee') is None:
            namespace = 'referees'
        elif self.has_role('Manager') and related_objects.get('Manager') is None:
            namespace = 'managers'
        elif self.has_role('Scorekeeper') and related_objects.get('Scorekeeper') is None:
            namespace = 'scorekeepers'
        else:
            namespace = None

        return namespace

    def __str__(self):
        return '{email} - {sport}'.format(email=self.user.email, sport=self.sport.name)
