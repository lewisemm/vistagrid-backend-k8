from rest_framework import serializers

from apiv1 import models


class PhotoSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        write_only=True,
        required=True,
        allow_empty_file=False,
        use_url=False
    )
    signed_url = serializers.URLField(read_only=True)

    class Meta:
        model = models.Photo
        fields = ('path', 'image', 'signed_url', 'photo_id')
        read_only_fields = ('path',)
