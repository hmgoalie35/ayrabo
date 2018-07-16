from django.db import models


class SportRegistrationManager(models.Manager):
    def create_for_user_and_sport(self, user, sport, roles):
        """
        Creates sport registrations for all roles. Does not check if a sport registration already exists for a role.
        """
        sport_registrations = []
        for role in roles:
            sport_registrations.append(self.create(user=user, sport=sport, role=role, is_complete=True))
        return sport_registrations
