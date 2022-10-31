import random

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from apiv1 import models, serializers

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = models.Photo.objects.all()
    serializer_class = serializers.PhotoSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            photo = models.Photo(**serializer.validated_data)
            # TODO: To be fixed when authentication is done.
            # retrieve a user id from provided token.
            photo.owner_id = int(random.random() * 100)
            photo.save()
            # TODO: add a second asynchronous step where photo is uploaded to
            # a service e.g. s3 or cloudinary
            return Response(
                serializers.PhotoSerializer(photo).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_BAD_REQUEST)
