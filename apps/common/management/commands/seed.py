from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.management.base import BaseCommand

from common.management.commands._utils import get_or_create, print_status
from common.management.seed_data.data import GENERIC_CHOICES, GENERIC_PENALTY_CHOICES, SPORTS
from common.models import GenericChoice
from penalties.models import GenericPenaltyChoice
from sports.models import Sport


class Command(BaseCommand):
    help = 'Top level seed command that calls other seed commands. Seeds initial data for the site.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding sports...')
        sports = []
        for sport_name in SPORTS:
            kwargs = {'name': sport_name}
            obj, created = get_or_create(Sport, get_kwargs=kwargs, create_kwargs=kwargs, exclude=['slug'])
            sports.append(obj)
            print_status(self.stdout, obj, created)
        self.stdout.write('\n')

        self.stdout.write('Seeding generic sport choices...')
        for sport in sports:
            choices = GENERIC_CHOICES.get(sport.name, [])
            for choice in choices:
                create_kwargs = choice.copy()
                create_kwargs.update({'content_object': sport})
                obj, created = get_or_create(
                    GenericChoice,
                    get_kwargs={
                        'short_value': choice.get('short_value'),
                        'content_type': ContentType.objects.get_for_model(sport),
                        'object_id': sport.id
                    },
                    create_kwargs=create_kwargs
                )
                print_status(self.stdout, obj, created)
        self.stdout.write('\n')

        self.stdout.write('Seeding generic penalty choices...')
        for sport in sports:
            choices = GENERIC_PENALTY_CHOICES.get(sport.name, [])
            for choice in choices:
                create_kwargs = choice.copy()
                create_kwargs.update({'content_object': sport})
                obj, created = get_or_create(
                    GenericPenaltyChoice,
                    get_kwargs={
                        'name': choice.get('name'),
                        'content_type': ContentType.objects.get_for_model(sport),
                        'object_id': sport.id
                    },
                    create_kwargs=create_kwargs
                )
                print_status(self.stdout, obj, created)
        self.stdout.write('\n')

        self.stdout.write('Seeding waffle switches, flags, samples...')
        call_command('seed_waffle')
        self.stdout.write('\n')
