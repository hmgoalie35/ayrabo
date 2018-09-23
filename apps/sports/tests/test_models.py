from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils.text import slugify

from ayrabo.utils.testing import BaseTestCase
from sports.models import Sport
from users.tests import UserFactory
from .factories.SportFactory import SportFactory
from .factories.SportRegistrationFactory import SportRegistrationFactory


class SportModelTests(BaseTestCase):
    # Slugs are auto generated from the name attribute, so the uniqueness of slugs makes sure names are also
    # unique for case insensitive ice Hockey and Ice Hockey will pass the uniqueness of the name field,
    # but won't pass uniqueness of slug field
    def test_unique_names_case_sensitive(self):
        Sport.objects.create(name='Ice Hockey')
        with self.assertRaises(IntegrityError):
            Sport.objects.create(name='Ice Hockey')

    def test_unique_slugs_case_insensitive(self):
        # Note trailing space, this prevents the unique constraint on name from failing this test. We want the slug
        # unique constraint to fail.
        SportFactory.create(name='ice Hockey ')
        with self.assertRaises(IntegrityError):
            SportFactory.create(name='ice hockey')

    def test_unique_names_case_insensitive(self):
        SportFactory.create(name='ice Hockey')
        with self.assertRaises(ValidationError):
            SportFactory.create(name='ice hockey')

    def test_slug_generation(self):
        ice_hockey = SportFactory.create(name='Ice hockey')
        self.assertEqual(ice_hockey.slug, slugify(ice_hockey.name))

    def test_default_ordering(self):
        ice_hockey = SportFactory(name='Ice Hockey')
        soccer = SportFactory(name='Soccer')
        baseball = SportFactory(name='Baseball')
        expected = [baseball, ice_hockey, soccer]
        self.assertListEqual(list(Sport.objects.all()), expected)

    def test_to_string(self):
        sport = SportFactory.build(name='Ice Hockey')
        self.assertEqual(str(sport), 'Ice Hockey')

    def test_name_converted_to_titlecase(self):
        sport = SportFactory.create(name='ice hockey')
        self.assertEqual(sport.name, 'Ice Hockey')


class SportRegistrationModelTests(BaseTestCase):
    def test_to_string(self):
        email = 'test@ayrabo.com'
        sport = SportFactory(name='Ice Hockey')
        user = UserFactory(email=email)
        sr = SportRegistrationFactory(user=user, sport=sport, role='player')

        self.assertEqual(str(sr), '{}: {} - {}'.format(email, 'Player', 'Ice Hockey'))

    def test_unique_together(self):
        user = UserFactory(email='testing@ayrabo.com')
        sport = SportFactory(name='Ice Hockey')
        SportRegistrationFactory(user=user, sport=sport, role='player')

        with self.assertRaises(IntegrityError):
            SportRegistrationFactory(user=user, sport=sport, role='player')
