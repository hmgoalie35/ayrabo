from django.core.exceptions import ValidationError

from escoresheet.utils.testing import BaseTestCase
from userprofiles.models import UserProfile
from .factories.UserProfileFactory import UserProfileFactory


class UserProfileModelTests(BaseTestCase):
    def test_invalid_height_format(self):
        invalid_heights = ['5 7', '5 7\"', '5\' 7', '5\' 12\"', '5\' 13\"', '5\'1\"']
        for invalid_height in invalid_heights:
            with self.assertRaisesMessage(ValidationError, UserProfile.INVALID_HEIGHT_MSG):
                UserProfileFactory.create(height=invalid_height).full_clean()

    def test_valid_height_format(self):
        valid_heights = ['5\' 7\"', '6\' 11\"', '6\' 10\"', '5\'']
        for valid_height in valid_heights:
            up = UserProfileFactory.create(height=valid_height)
            self.assertIsNone(up.full_clean())

    def test_min_weight(self):
        # MIN_WEIGHT is currently 1
        with self.assertRaisesMessage(ValidationError, 'Ensure this value is greater than or equal to 1.'):
            UserProfileFactory(weight=0).full_clean()
            UserProfileFactory(weight=-1).full_clean()

    def test_max_weight(self):
        # MAX_WEIGHT is currently 400
        with self.assertRaisesMessage(ValidationError, 'Ensure this value is less than or equal to 400.'):
            UserProfileFactory(weight=401).full_clean()

    def test_weight_floating_point_number(self):
        with self.assertRaisesMessage(ValidationError, 'Ensure this value is greater than or equal to 1.'):
            UserProfileFactory(weight=.5).full_clean()
            UserProfileFactory(weight=-.5).full_clean()

    def test_valid_weight(self):
        up = UserProfileFactory(weight=200)
        self.assertIsNone(up.full_clean())

    def test_to_string(self):
        up = UserProfileFactory.create()
        self.assertEqual(str(up), up.user.email)
