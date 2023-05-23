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
    permissions as api_permissions
)


class PhotoViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.PhotoSerializer
    permission_classes = [api_permissions.OnlyOwnerCanAccess]

    def get_queryset(self):
        owner_id = self.request.headers.get('Owner-Id', None)
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
            owner_id = request.headers.get('Owner-Id', None)
            if utils.owner_id_header_is_valid(owner_id):
                img = request.data['image']
                fmt = "%Y_%m_%d__%H_%M_%S"
                current_time = datetime.datetime.now()
                formatted_time = datetime.datetime.strftime(current_time, fmt)
                file_name = f'photos/{formatted_time}-{img.name}'
                try:
                    with transaction.atomic():
                        photo = models.Photo(path=file_name)
                        photo.owner_id = owner_id
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
            return Response(
                {'error': 'Invalid value for "Owner-Id" header.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        owner_id = request.headers.get('Owner-Id', None)
        try:
            photo_to_delete = models.Photo.objects.get(pk=pk)
            if not utils.owner_id_header_is_valid(owner_id):
                return Response(
                    {'error': 'Invalid value for "Owner-Id" header.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            owner_id = int(owner_id)
            if photo_to_delete.owner_id != owner_id:
                return Response(
                    {'error': 'Access to this resource is restricted to owner.'},
                    status=status.HTTP_403_FORBIDDEN
                )
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
