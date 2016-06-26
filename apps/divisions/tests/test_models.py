from django.test import TestCase
from .factories.DivisionFactory import DivisionFactory
from divisions.models import Division
from django.db.utils import IntegrityError
from escoresheet.testing_utils import is_queryset_in_alphabetical_order


class DivisionModelTests(TestCase):
    def test_default_ordering(self):
        DivisionFactory.create_batch(5)
        self.assertTrue(is_queryset_in_alphabetical_order(Division.objects.all(), 'name'))

    def test_to_string(self):
        metro_division = DivisionFactory.create(name='Metropolitan Division')
        self.assertEqual(str(metro_division), 'Metropolitan Division')

    def test_unique_division_name(self):
        DivisionFactory.create(name='Pacific Division')
        with self.assertRaises(IntegrityError, msg='UNIQUE constraint failed: divisions_division.name'):
            DivisionFactory.create(name='Pacific Division')
