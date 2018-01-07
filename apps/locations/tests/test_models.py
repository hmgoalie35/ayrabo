from django.core.exceptions import ValidationError
from django.db import IntegrityError

from escoresheet.utils.testing import BaseTestCase
from locations.tests import TeamLocationFactory
from teams.tests import TeamFactory
from . import LocationFactory


class LocationModelTests(BaseTestCase):
    def test_phone_number_regex_valid(self):
        location = LocationFactory(phone_number='(516) 123-4567')
        self.assertEqual(location.phone_number, '(516) 123-4567')

    def test_phone_number_regex_invalid(self):
        with self.assertRaisesMessage(ValidationError, 'Enter a valid phone number.'):
            LocationFactory(phone_number='2345671890')

    def test_website_invalid_scheme(self):
        with self.assertRaisesMessage(ValidationError, 'Enter a valid URL.'):
            LocationFactory(website='ftp://www.example.com')

    def test_unique_name(self):
        LocationFactory(name='Nassau Veterans Memorial Coliseum')
        with self.assertRaises(IntegrityError):
            LocationFactory(name='Nassau Veterans Memorial Coliseum')

    def test_unique_slug(self):
        LocationFactory(name='Nassau Veterans Memorial Coliseum')
        with self.assertRaises(IntegrityError):
            # Note the space at the end of the name, it allows the name to pass the name's unique constraint
            LocationFactory(name='Nassau Veterans Memorial Coliseum ')

    def test_slug_generation(self):
        location = LocationFactory(name='Nassau Veterans Memorial Coliseum')
        self.assertEqual(location.slug, 'nassau-veterans-memorial-coliseum')

    def test_to_string(self):
        location = LocationFactory(name='Nassau Veterans Memorial Coliseum')
        self.assertEqual(str(location), 'Nassau Veterans Memorial Coliseum')


class TeamLocationModelTests(BaseTestCase):
    def test_unique_together_team_location(self):
        team = TeamFactory(name='New York Islanders')
        location = LocationFactory(name='Nassau Veterans Memorial Coliseum')
        TeamLocationFactory(team=team, location=location)
        with self.assertRaises(IntegrityError):
            TeamLocationFactory(team=team, location=location, primary=True)

    def test_to_string(self):
        team = TeamFactory(name='New York Islanders')
        location = LocationFactory(name='Nassau Veterans Memorial Coliseum')
        tl = TeamLocationFactory(team=team, location=location)
        self.assertEqual(str(tl), 'New York Islanders: Nassau Veterans Memorial Coliseum')
