from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.text import slugify

import coaches as coaches_app
import managers as managers_app
import players as players_app
import referees as referees_app


class Sport(models.Model):
    name = models.CharField(max_length=255, unique=True,
                            error_messages={'unique': 'Sport with this name already exists (case-insensitive)'})
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Created')

    class Meta:
        ordering = ['name']

    def clean(self):
        self.name = self.name.title()
        self.slug = slugify(self.name)
        self.save()

    def __str__(self):
        return self.name


class SportRegistration(models.Model):
    """
    Model used to store what roles a user has for a sport. A user chooses to register for a sport and has the option to
    choose what roles(s) they want for a specific sport

    i.e. user John might want to be a Player and Referee for Ice Hockey, but only wants to be a Coach for Soccer. There
    would b 2 SportRegistration objects, both tied to John but one is for Ice Hockey with roles_mask corresponding to
    Player and Referee and another tied to sport Soccer with a roles_mask corresponding to Coach
    """

    ROLES = ['Player', 'Coach', 'Referee', 'Manager']

    user = models.ForeignKey(User)
    sport = models.ForeignKey(Sport)
    roles_mask = models.SmallIntegerField(default=0, verbose_name='Roles Mask')
    # Signifies if each Coach, Referee, Manager, HockeyPlayer, etc. object has been created for all roles of this model
    is_complete = models.BooleanField(default=False, verbose_name='Is Registration Complete')

    class Meta:
        ordering = ['user']
        unique_together = (
            ('user', 'sport'),
        )

    def get_absolute_url(self):
        return reverse('sport:update_sport_registration', kwargs={'pk': self.pk})

    def set_roles(self, roles, append=False):
        """
        Given a list of roles (taken from ROLES) creates a mask (int) that represents the roles currently valid for this
        user for a given sport
        :param append: Set to True to indicate you want to append roles to any existent roles, set to False to overwrite
        any existing roles with roles
        :param roles: The role(s) to add
        """

        assert type(roles) == list

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

    def get_related_role_objects(self):
        """
        This function iterates through all of the roles for the sport registration and retrieves the appropriate
        object that goes with the role. i.e. Roles Coach and Manager are set, so this function will fetch the Coach
        and Manager objects for the given user and sport
        :return: A dictionary where the keys are the role (Player, Coach, etc.) and the value is the associated object
        """

        obj_role_mappings = {}
        roles = self.roles
        user = self.user
        for role in roles:
            if role == 'Player':
                sport_name = self.sport.name
                if 'Hockey' in sport_name:
                    players = players_app.models.HockeyPlayer.objects.filter(user=user,
                                                                             sport=self.sport).select_related('team')
                elif sport_name == 'Basketball':
                    players = players_app.models.BasketballPlayer.objects.filter(user=user,
                                                                                 sport=self.sport).select_related(
                        'team')
                elif sport_name == 'Baseball':
                    players = players_app.models.BaseballPlayer.objects.filter(user=user,
                                                                               sport=self.sport).select_related('team')
                obj_role_mappings['Player'] = players.first()
            elif role == 'Coach':
                coaches = coaches_app.models.Coach.objects.filter(user=user,
                                                                  team__division__league__sport=self.sport).select_related(
                    'team')
                obj_role_mappings['Coach'] = coaches.first()
            elif role == 'Manager':
                managers = managers_app.models.Manager.objects.filter(user=user,
                                                                      team__division__league__sport=self.sport).select_related(
                    'team')
                obj_role_mappings['Manager'] = managers.first()
            elif role == 'Referee':
                referees = referees_app.models.Referee.objects.filter(user=user,
                                                                      league__sport=self.sport).select_related('league')
                obj_role_mappings['Referee'] = referees.first()
        return obj_role_mappings

    def __str__(self):
        return '{email} - {sport}'.format(email=self.user.email, sport=self.sport.name)
