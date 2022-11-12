import asyncio
import datetime
import random

from rest_framework import viewsets, status
from rest_framework.response import Response

from apiv1 import models, serializers, tasks

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = models.Photo.objects.all()
    serializer_class = serializers.PhotoSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            img = request.data['image']
            fmt = "%Y_%m_%d__%H_%M_%S"
            current_time = datetime.datetime.now()
            formatted_time = datetime.datetime.strftime(current_time, fmt)
            file_name = f'photos/{formatted_time}-{img.name}'
            photo = models.Photo(path=file_name)
            # TODO: To be fixed when authentication is done.
            # (retrieve a user id from provided token.)
            photo.owner_id = int(random.random() * 100)
            photo.save()
            asyncio.run(
                tasks.async_upload_to_s3_wrapper(
                    img, file_name, img.content_type)
            )
            return Response(
                serializers.PhotoSerializer(photo).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        try:
            # ---------------- TODO: add atomic transaction ---------------------
            photo_to_delete = self.queryset.get(pk=pk)
            object_key = photo_to_delete.path
            photo_to_delete.delete()
            tasks.async_delete_object_from_s3.delay(object_key)
            # ---------------- end atomic transaction ---------------------
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        except models.Photo.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
