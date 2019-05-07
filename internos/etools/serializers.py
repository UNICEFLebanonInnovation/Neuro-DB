
from rest_framework import serializers
from .models import PartnerOrganization


class PartnerOrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = PartnerOrganization
        fields = (
            'id',
            'comments'
        )
