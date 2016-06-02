from django.test import TestCase
from .factories.SportFactory import SportFactory
from django.db.utils import IntegrityError


class SportModelTests(TestCase):

    def test_unique_names_case_sensitive(self):
        SportFactory.create(name='Hockey')
        with self.assertRaises(IntegrityError, msg='UNIQUE constraint failed: sports_sport.name'):
            SportFactory.create(name='Hockey')

    def test_unique_names_case_insensitive(self):
        SportFactory.create(name='Hockey')
        with self.assertRaises(IntegrityError, msg='UNIQUE constraint failed: sports_sport.name'):
            SportFactory.create(name='hockey')

    def test_unique_slugs_case_sensitive(self):
        SportFactory.create(name='hockey')
        with self.assertRaises(IntegrityError, msg='UNIQUE constraint failed: sports_sport.slug'):
            SportFactory.create(name='hockey')

    def test_unique_slugs_case_insensitive(self):
        SportFactory.create(name='hockey')
        with self.assertRaises(IntegrityError, msg='UNIQUE constraint failed: sports_sport.slug'):
            SportFactory.create(name='hockey')
