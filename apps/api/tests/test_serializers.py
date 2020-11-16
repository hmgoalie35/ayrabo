from collections import OrderedDict
from unittest import mock

from rest_framework import serializers

from api.serializers import (
    AbstractBulkCreateModelSerializer,
    AbstractBulkDeleteModelSerializer,
    AbstractBulkUpdateModelSerializer,
    BulkCreateUpdateDeleteListSerializer,
)
from ayrabo.utils.testing import BaseAPITestCase
from ayrabo.utils.testing.models import DummyModel


class BulkUpdateDummyModelSerializer(AbstractBulkUpdateModelSerializer):
    class Meta(AbstractBulkUpdateModelSerializer.Meta):
        model = DummyModel
        fields = ('id', 'name', 'count')


class BulkDeleteDummyModelSerializer(AbstractBulkDeleteModelSerializer):
    class Meta(AbstractBulkDeleteModelSerializer.Meta):
        model = DummyModel


class BulkCreateUpdateDeleteListSerializerTests(BaseAPITestCase):
    def setUp(self):
        self.instance1 = DummyModel.objects.create(name='Isles', count=1)
        self.instance2 = DummyModel.objects.create(name='Rags', count=2)
        self.mock_view = mock.Mock()
        self.mock_view.get_queryset.return_value = DummyModel.objects.filter(
            id__in=[self.instance1.id, self.instance2.id]
        )
        self.context = {'view': self.mock_view}

    def test_bulk_update(self):
        data = [{'id': self.instance1.id, 'count': 100}, {'id': self.instance2.id, 'name': 'Flyers'}]
        serializer = BulkCreateUpdateDeleteListSerializer(
            child=BulkUpdateDummyModelSerializer(context=self.context),
            data=data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        instances = serializer.bulk_update()

        self.instance1.refresh_from_db()
        self.instance2.refresh_from_db()

        self.assertEqual(len(instances), 2)
        self.assertEqual(self.instance1.name, 'Isles')
        self.assertEqual(self.instance1.count, 100)
        self.assertEqual(self.instance2.name, 'Flyers')
        self.assertEqual(self.instance2.count, 2)

        self.assertIsNotNone(serializer.validated_data[0].get('id'))

    def test_bulk_delete(self):
        data = [{'id': self.instance1.id}, {'id': self.instance2.id}]
        serializer = BulkCreateUpdateDeleteListSerializer(
            child=BulkDeleteDummyModelSerializer(context=self.context),
            data=data
        )
        serializer.is_valid(raise_exception=True)

        num_deleted, extra_info = serializer.bulk_delete()

        self.assertEqual(num_deleted, 2)
        self.assertDictEqual(extra_info, {'testing.DummyModel': 2})

    def test_to_representation(self):
        instance3 = DummyModel.objects.create(name='Canes', count=11)
        # We're explicitly passing data to `to_representation` so we don't need to go crazy making this serializer
        # perfect
        serializer = BulkCreateUpdateDeleteListSerializer(child=BulkUpdateDummyModelSerializer(context=self.context))

        result = serializer.to_representation([{'id': self.instance1}, OrderedDict(id=self.instance2), instance3])

        self.assertListEqual(result, [
            {'id': self.instance1.id, 'name': 'Isles', 'count': 1},
            {'id': self.instance2.id, 'name': 'Rags', 'count': 2},
            {'id': instance3.id, 'name': 'Canes', 'count': 11},
        ])


class AbstractBulkCreateModelSerializerTests(BaseAPITestCase):
    def test_meta(self):
        serializer = AbstractBulkCreateModelSerializer()
        self.assertIs(serializer.Meta.list_serializer_class, BulkCreateUpdateDeleteListSerializer)


class AbstractBulkUpdateModelSerializerTests(BaseAPITestCase):
    def setUp(self):
        mock_view = mock.Mock()
        mock_view.get_queryset.return_value = []
        self.serializer = BulkUpdateDummyModelSerializer(context={'view': mock_view})

    def test_init(self):
        # DRF removes the default id field so we need to explicitly set it so the serializer actually validates the ids
        # are valid, etc
        self.assertIs(type(self.serializer.fields.get('id')), serializers.PrimaryKeyRelatedField)

    def test_validate(self):
        with self.assertRaisesMessage(serializers.ValidationError, 'This field is required.'):
            self.serializer.validate({})

        self.assertDictEqual(self.serializer.validate({'id': 1}), {'id': 1})


class AbstractBulkDeleteModelSerializerTests(BaseAPITestCase):
    def setUp(self):
        mock_view = mock.Mock()
        mock_view.get_queryset.return_value = []
        self.serializer = BulkDeleteDummyModelSerializer(context={'view': mock_view})

    def test_init(self):
        self.assertIs(type(self.serializer.fields.get('id')), serializers.PrimaryKeyRelatedField)

    def test_meta(self):
        self.assertTupleEqual(self.serializer.Meta.fields, ('id',))
        self.assertIs(self.serializer.Meta.list_serializer_class, BulkCreateUpdateDeleteListSerializer)
