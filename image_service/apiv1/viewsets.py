import asyncio
import datetime

from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response

from apiv1 import (
    models,
    serializers,
    tasks,
    utils,
    permissions as api_permissions,
    authentication as api_auth
)


class PhotoViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.PhotoSerializer
    permission_classes = [api_permissions.OnlyOwnerCanAccess]
    authentication_classes = [api_auth.CustomAuthentication]

    def get_queryset(self):
        owner_id = self.request.user
        if owner_id:
            owner_id = int(owner_id)
            return models.Photo.objects.filter(owner_id=owner_id)
        return models.Photo.objects.none()

    def get_object(self):
        obj = models.Photo.objects.get(pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            img = request.data['image']
            fmt = "%Y_%m_%d__%H_%M_%S"
            current_time = datetime.datetime.now()
            formatted_time = datetime.datetime.strftime(current_time, fmt)
            file_name = f'photos/{formatted_time}-{img.name}'
            try:
                with transaction.atomic():
                    photo = models.Photo(path=file_name)
                    photo.owner_id = request.user
                    photo.save()
                    transaction.on_commit(
                        lambda: asyncio.run(
                            tasks.async_upload_to_s3_wrapper(
                                img, file_name, img.content_type
                            )
                        )
                    )
                return Response(
                    serializers.PhotoSerializer(photo).data,
                    status=status.HTTP_202_ACCEPTED
                )
            except Exception:
                return Response(
                    {'error': 'Request could not be completed.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        try:
            photo_to_delete = models.Photo.objects.get(pk=pk)
            self.check_object_permissions(request, photo_to_delete)
            try:
                with transaction.atomic():
                    object_key = photo_to_delete.path
                    photo_to_delete.delete()
                    transaction.on_commit(
                        tasks.async_delete_object_from_s3.s(object_key).delay
                    )
                return Response({}, status=status.HTTP_204_NO_CONTENT)
            except Exception:
                return Response(
                    {'error': 'Request could not be completed.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except models.Photo.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
