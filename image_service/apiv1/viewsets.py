import asyncio
import datetime
import json
import random

from rest_framework import viewsets, status
from rest_framework.response import Response

from apiv1 import models, serializers, tasks, utils

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = models.Photo.objects.all()
    serializer_class = serializers.PhotoSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # TODO: Define this logic in a function to avoid possible DRY
            #  principle violation
            # TODO: Look into caching
            # ----------------------------------------------------------
            token = request.headers.get('Authorization', None)
            if not token:
                return Response(
                    {'error': 'Authorization JWT token is required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            resp = utils.get_user_id_from_auth_service(token)
            if resp.code != 200:
                return Response(
                    {'error': 'Authorization JWT token is invalid'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data = resp.readlines()
            data = json.loads(data[0].decode('utf-8'))
            owner_id = data['user_id']
            # ----------------------------------------------------------
            img = request.data['image']
            fmt = "%Y_%m_%d__%H_%M_%S"
            current_time = datetime.datetime.now()
            formatted_time = datetime.datetime.strftime(current_time, fmt)
            file_name = f'photos/{formatted_time}-{img.name}'
            photo = models.Photo(path=file_name)
            photo.owner_id = owner_id
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

    def list(self, request):
        # directly modifying the contents of queryset will lead to unexpected
        # behaviour. create a copy of queryset and modify that instead.
        qset = self.queryset[::]
        for photo in qset:
            photo.signed_url = tasks.generate_presigned_url(photo.path)
        return Response(
            self.serializer_class(qset, many=True).data,
            status=status.HTTP_200_OK
        )

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
