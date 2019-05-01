from rest_framework import serializers

from .models import Location, LocationType


class LocationTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = LocationType
        fields = '__all__'


class LocationLightSerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)
    name = serializers.SerializerMethodField()
    type = LocationTypeSerializer()

    @staticmethod
    def get_name(obj):
        return '{} [{} - {}]'.format(obj.name, obj.type.name, obj.p_code)

    class Meta:
        model = Location
        fields = (
            'id',
            'name',
            'p_code',
            'type',
        )


class LocationSerializer(LocationLightSerializer):

    geo_point = serializers.StringRelatedField()

    class Meta(LocationLightSerializer.Meta):
        model = Location
        fields = LocationLightSerializer.Meta.fields + ('geo_point', 'parent')


class LocationExportSerializer(serializers.ModelSerializer):
    location_type = serializers.CharField(source='type.name')
    geo_point = serializers.StringRelatedField()
    point = serializers.StringRelatedField()

    class Meta:
        model = Location
        fields = "__all__"


class LocationExportFlatSerializer(serializers.ModelSerializer):
    location_type = serializers.CharField(source='type.name')
    geom = serializers.SerializerMethodField()
    point = serializers.StringRelatedField()

    class Meta:
        model = Location
        fields = "__all__"

    def get_geom(self, obj):
        return obj.geom.point_on_surface if obj.geom else ""

