from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import get_storage_class
from django.utils.six import BytesIO
from easy_thumbnails import files

from api.utils.serializer_fields import EasyThumbnailField
from ayrabo.utils.testing import BaseAPITestCase


class EasyThumbnailFieldTests(BaseAPITestCase):
    def _create_image(self, file_name, image_format='JPEG'):
        storage = get_storage_class()()
        data = BytesIO()
        img = Image.new('RGB', (800, 600))
        img.save(data, image_format)
        data.seek(0)
        image_file = ContentFile(data.read())
        fname = storage.save(file_name, image_file)
        return storage, fname

    def _get_thumbnailer(self, file_name):
        storage, fname = self._create_image(file_name)
        thumbnailer = files.get_thumbnailer(storage, fname)
        return thumbnailer

    def test_alias_kwarg_required(self):
        with self.assertRaisesMessage(AssertionError, 'The alias kwarg is required.'):
            EasyThumbnailField()

    def test_to_representation_alias_dne(self):
        thumbnailer = self._get_thumbnailer('image.jpeg')
        field = EasyThumbnailField(alias='dne')
        to_repr = field.to_representation(thumbnailer)

        self.assertIsNone(to_repr)

    def test_to_representation(self):
        thumbnailer = self._get_thumbnailer('image.jpeg')
        field = EasyThumbnailField(alias='sm')
        to_repr = field.to_representation(thumbnailer)

        self.assertTrue(field.read_only)
        self.assertIn('/media/thumbnails', to_repr)
