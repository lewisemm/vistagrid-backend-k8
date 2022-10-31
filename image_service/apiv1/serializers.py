from rest_framework import serializers

from apiv1 import models


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Photo
        fields = ('path',)
