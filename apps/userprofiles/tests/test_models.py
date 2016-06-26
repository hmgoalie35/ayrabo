from django.core.exceptions import ValidationError
from django.test import TestCase

from userprofiles.models import MAX_WEIGHT
from .factories.UserProfileFactory import UserProfileFactory
from userprofiles.models import UserProfile


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
        invalid_weights = [-1, 0, -100, -.5, .5, MAX_WEIGHT + 1]
        for invalid_weight in invalid_weights:
            with self.assertRaises(ValidationError, msg='Weight must be greater than zero and less than 400'):
                UserProfileFactory.create(weight=invalid_weight).full_clean()

    def test_valid_weight(self):
        valid_weights = [1, 2, 100, 30, 130, MAX_WEIGHT - 1, MAX_WEIGHT]
        for valid_weight in valid_weights:
            up = UserProfileFactory.create(weight=valid_weight)
            self.assertIsNone(up.full_clean())

    def test_to_string(self):
        up = UserProfileFactory.create()
        self.assertEqual(str(up), up.user.email)

    def test_current_available_roles(self):
        self.assertListEqual(UserProfile.ROLES, ['Player', 'Coach', 'Referee', 'Manager'])

    def test_default_role_mask(self):
        up = UserProfileFactory.create()
        self.assertEqual(up.roles_mask, 0)

    def test_set_roles_param_not_a_list(self):
        up = UserProfileFactory.create()
        with self.assertRaises(AssertionError):
            up.set_roles(('Player', 'Manager'))

    def test_set_roles_no_append(self):
        up = UserProfileFactory.create()
        up.set_roles(['Player', 'Manager'])
        self.assertEqual(up.roles_mask, 9)

    def test_set_roles_append(self):
        up = UserProfileFactory.create()
        up.set_roles(['Player', 'Manager'])
        up.set_roles(['Coach'], append=True)
        self.assertEqual(up.roles_mask, 11)

    def test_set_roles_invalid_role(self):
        up = UserProfileFactory.create()
        up.set_roles(['Referee', 'Invalid'])
        self.assertEqual(up.roles, ['Referee'])

    def test_set_roles_empty_list(self):
        up = UserProfileFactory.create()
        up.set_roles([])
        self.assertEqual(up.roles_mask, 0)

    def test_roles_property(self):
        roles = ['Player', 'Manager']
        up = UserProfileFactory.create()
        up.set_roles(roles)
        self.assertEqual(up.roles, roles)

    def test_has_role_true(self):
        roles = ['Player', 'Manager']
        up = UserProfileFactory.create()
        up.set_roles(roles)
        self.assertTrue(up.has_role('Player'))
        self.assertTrue(up.has_role('manager'))

    def test_has_role_false(self):
        roles = ['Coach', 'Manager']
        up = UserProfileFactory.create()
        up.set_roles(roles)
        self.assertFalse(up.has_role('Player'))
        self.assertFalse(up.has_role('InvalidRole'))
