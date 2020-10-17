from collections import OrderedDict

from rest_framework import serializers


class BulkCreateUpdateDeleteListSerializer(serializers.ListSerializer):
    pk_field = 'id'

    def create(self, validated_data):
        return super().create(validated_data)

    def bulk_update(self):
        instances = []
        for data in self.validated_data:
            instance = data.pop(self.pk_field)
            self.child.update(instance, data)
            # We could `.copy` `self.validated_data` so we don't need to add this back but I think this is fine as is
            data.update({self.pk_field: instance})
            instances.append(instance)
        return instances

    def bulk_delete(self):
        model_cls = self.child.Meta.model
        ids = []
        for data in self.validated_data:
            instance = data.pop(self.pk_field)
            ids.append(getattr(instance, self.pk_field))
        # Returns # of objs deleted and a dictionary with the number of deletions per object type
        return model_cls.objects.filter(id__in=ids).delete()

    def to_representation(self, data):
        instances = []
        for d in data:
            if isinstance(d, (dict, OrderedDict)):
                # `d` is a dict of id -> instance
                instances.append(d.get('id'))
            else:
                instances.append(d)
        return super().to_representation(instances)


class AbstractBulkCreateModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        list_serializer_class = BulkCreateUpdateDeleteListSerializer


class AbstractBulkUpdateModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        self.fields['id'] = serializers.PrimaryKeyRelatedField(queryset=self.Meta.model.objects.all())
        super().__init__(*args, **kwargs)

    def validate(self, data):
        # There's some weirdness with partial=True that doesn't actually validate a payload like [{}] includes id
        if not data.get('id'):
            raise serializers.ValidationError({'id': 'This field is required.'})
        return data

    class Meta:
        model = None  # Remember to update me
        fields = ('id',)  # Remember to update me but still include `id`
        list_serializer_class = BulkCreateUpdateDeleteListSerializer


class AbstractBulkDeleteModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        self.fields['id'] = serializers.PrimaryKeyRelatedField(queryset=self.Meta.model.objects.all())
        super().__init__(*args, **kwargs)

    class Meta:
        model = None  # Remember to update me
        fields = ('id',)
        list_serializer_class = BulkCreateUpdateDeleteListSerializer
