from easy_thumbnails.files import get_thumbnailer
from rest_framework import serializers


class EasyThumbnailField(serializers.ImageField):
    def __init__(self, *args, **kwargs):
        self.alias = kwargs.pop('alias', None)
        assert self.alias is not None, 'The alias kwarg is required.'
        kwargs.update({
            'read_only': True
        })
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        thumbnailer = get_thumbnailer(value)
        try:
            # This can throw a `KeyError` if the alias hasn't been configured.
            thumb = thumbnailer[self.alias]
        except KeyError:
            thumb = None
        return super().to_representation(thumb)
