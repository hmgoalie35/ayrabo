from django.core.exceptions import ValidationError
from django.test import TestCase
from userprofiles.models import MAX_WEIGHT

from .factories.UserProfileFactory import UserProfileFactory


class UserProfileModelTests(TestCase):
    def test_invalid_height_format(self):
        invalid_heights = ['5 7', '5 7\"', '5\' 7', '5\' 12\"', '5\' 13\"', '5\'1\"']
        for invalid_height in invalid_heights:
            with self.assertRaises(ValidationError, msg='Invalid format, please use the following format: 5\' 7\"'):
                UserProfileFactory.create(height=invalid_height).full_clean()

    def test_valid_height_format(self):
        valid_heights = ['5\' 7\"', '6\' 11\"', '6\' 10\"', '5\'']
        for valid_height in valid_heights:
            up = UserProfileFactory.create(height=valid_height)
            self.assertIsNone(up.full_clean())

    def test_invalid_weight(self):
        invalid_weights = [-1, 0, -100, -.5, .5, MAX_WEIGHT+1]
        for invalid_weight in invalid_weights:
            with self.assertRaises(ValidationError, msg='Weight must be greater than zero and less than 400'):
                UserProfileFactory.create(weight=invalid_weight).full_clean()

    def test_valid_weight(self):
            valid_weights = [1, 2, 100, 30, 130, MAX_WEIGHT-1, MAX_WEIGHT]
            for valid_weight in valid_weights:
                up = UserProfileFactory.create(weight=valid_weight)
                self.assertIsNone(up.full_clean())
