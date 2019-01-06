from easy_thumbnails.files import get_thumbnailer
from rest_framework import serializers


class EasyThumbnailField(serializers.ImageField):
    def __init__(self, *args, **kwargs):
        self.alias = kwargs.pop('alias', None)
        assert self.alias is not None, 'alias is required'
        kwargs.update({
            'read_only': True
        })
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        # TODO Error handling
        thumb = get_thumbnailer(value)[self.alias]
        return super().to_representation(thumb)
