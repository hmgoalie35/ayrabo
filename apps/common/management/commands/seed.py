from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from common.models import GenericChoice
from penalties.models import GenericPenaltyChoice
from sports.models import Sport


SPORTS = ['Ice Hockey', 'Baseball']
GENERIC_CHOICES = {
    'Ice Hockey': [
        # Game types
        {'short_value': 'exhibition', 'long_value': 'Exhibition', 'type': 'game_type'},
        {'short_value': 'league', 'long_value': 'League', 'type': 'game_type'},
        # Game point values
        {'short_value': '0', 'long_value': '0', 'type': 'game_point_value'},
        {'short_value': '1', 'long_value': '1', 'type': 'game_point_value'},
        {'short_value': '2', 'long_value': '2', 'type': 'game_point_value'},
    ]
}

# TODO Correctly generate these from LIAHL/NHL rulebooks. These are just for
GENERIC_PENALTY_CHOICES = {
    'Ice Hockey': [
        {'name': 'Abuse of officials', 'description': ''},
        {'name': 'Aggressor penalty', 'description': ''},
        {'name': 'Attempt to injure', 'description': ''},
        {'name': 'Biting', 'description': ''},
        {'name': 'Boarding', 'description': ''},
        {'name': 'Butt ending', 'description': ''},
        {'name': 'Broken stick', 'description': ''},
        {'name': 'Charging', 'description': ''},
        {'name': 'Checking from behind', 'description': ''},
        {'name': 'Clipping', 'description': ''},
        {'name': 'Cross checking', 'description': ''},
        {'name': 'Delay of game', 'description': ''},
        {'name': 'Diving', 'description': ''},
        {'name': 'Elbowing', 'description': ''},
        {'name': 'Eye gouging', 'description': ''},
        {'name': 'Fighting', 'description': ''},
        {'name': 'Goaltender interference', 'description': ''},
        {'name': 'Goaltender leaving the crease', 'description': ''},
        {'name': 'Head butting', 'description': ''},
        {'name': 'High sticking', 'description': ''},
        {'name': 'Holding', 'description': ''},
        {'name': 'Holding the stick', 'description': ''},
        {'name': 'Hooking', 'description': ''},
        {'name': 'Illegal check to the head', 'description': ''},
        {'name': 'Illegal equipment', 'description': ''},
        {'name': 'Instigator', 'description': ''},
        {'name': 'Interference', 'description': ''},
        {'name': 'Third man in', 'description': ''},
        {'name': 'Kicking', 'description': ''},
        {'name': 'Kneeing', 'description': ''},
        {'name': 'Roughing', 'description': ''},
        {'name': 'Slashing', 'description': ''},
        {'name': 'Slew footing', 'description': ''},
        {'name': 'Spearing', 'description': ''},
        {'name': 'Starting the wrong lineup', 'description': ''},
        {'name': 'Substitution infraction', 'description': ''},
        {'name': 'Throwing the stick', 'description': ''},
        {'name': 'Too many men', 'description': ''},
        {'name': 'Tripping', 'description': ''},
        {'name': 'Unsportsmanlike conduct', 'description': ''},
    ]
}

SITE_NAME = 'escoresheet.com'


class Command(BaseCommand):
    help = 'Configures the project with sports, etc.'

    def print_status(self, obj, created):
        self.stdout.write('{} {}'.format('Created' if created else 'Skipped', obj))

    def handle(self, *args, **options):

        self.stdout.write('Updating default site name...')
        try:
            site = Site.objects.get(name='example.com')
            site.domain = SITE_NAME
            site.name = SITE_NAME
            site.save()
        except Site.DoesNotExist:
            pass
        print()

        # TODO Create leagues/teams, seasons... Cron job for seasons?
        self.stdout.write('Seeding sports...')
        sports = []
        for sport in SPORTS:
            obj, created = Sport.objects.get_or_create(name=sport)
            obj.full_clean()
            sports.append(obj)
            self.print_status(obj, created)
        print()

        self.stdout.write('Seeding generic sport choices...')
        for sport in sports:
            choices = GENERIC_CHOICES.get(sport.name, [])
            for choice in choices:
                choice.update({'content_object': sport})
                try:
                    obj = GenericChoice.objects.create(**choice)
                    created = True
                except IntegrityError:
                    obj = choice.get('long_value')
                    created = False
                self.print_status(obj, created)
        print()

        self.stdout.write('Seeding generic penalty choices...')
        for sport in sports:
            choices = GENERIC_PENALTY_CHOICES.get(sport.name, [])
            for choice in choices:
                choice.update({'content_object': sport})
                try:
                    obj = GenericPenaltyChoice.objects.create(**choice)
                    created = True
                except IntegrityError:
                    obj = choice.get('name')
                    created = False
                self.print_status(obj, created)
