import os
import pathlib
import random
from unittest.mock import patch, call

import faker
from django.conf import settings
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient


from apiv1 import models


class MockUserServiceResponse:
    """
    Mock response from the user_service.
    """
    def __init__(self):
        self.code = 200

    def readlines(self):
        return ['{"user_id": 2}'.encode('utf-8')]


class TestPhotos(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.fake = faker.Faker()
        test_png_relative_path = pathlib.Path('apiv1/tests/uploadable/test.png')
        self.test_png_path = os.path.join(
            settings.BASE_DIR.parent,
            test_png_relative_path
        )

    def tearDown(self):
        del self.client
        del self.fake

    def generate_owner_fake_photo_entries(self, owner_id):
        """
        Generate random fake photo entries that belong to user of
        user_id == owner_id.
        """
        # create fake entries
        count = int(random.random() * 10) + 1
        photo_ids = []
        for i in range(count):
            data = {
                'path': self.fake.file_name(),
                'owner_id': owner_id
            }
            photo = models.Photo(**data)
            photo.save()
            photo_ids.append(photo.photo_id)
        return count, photo_ids

    def generate_random_fake_photo_entries(self, owner_id):
        """
        Generates random fake photo entries that do not belong to user of
        user_id == owner_id.
        """
        # create fake entries
        count = int(random.random() * 10) + 1
        photo_ids = []
        for i in range(count):
            data = {
                'path': self.fake.file_name(),
                'owner_id': self.get_random_user_id()
            }
            # ensure this photo entry does not belong to owner_id
            while data['owner_id'] == owner_id:
                data['owner_id'] = self.get_random_user_id()
            photo = models.Photo(**data)
            photo.save()
            photo_ids.append(photo.photo_id)
        return count, photo_ids

    def get_uploaded_test_png(self):
        photo = open(self.test_png_path, 'rb')
        photo = File(photo)
        photo = SimpleUploadedFile('uploaded.png', photo.read(), content_type='multipart/form-data')
        return photo

    def get_random_user_id(self):
        """
        Generates and returns a random user_id that falls between 1 - 1000.
        """
        return int(random.random() * 1000)

    @patch('apiv1.tasks.generate_presigned_url')
    @patch('apiv1.tasks.async_upload_to_s3_wrapper')
    def test_post_photo(
        self, async_wrapper, generate_presigned_url
    ):
        """
        Test photo create functionality.
        """
        # no photos exist yet
        photos = models.Photo.objects.all()
        self.assertEqual(len(photos), 0)
        url = reverse('photo-list')
        data = {
            'image': self.get_uploaded_test_png()
        }
        current_user_id = self.get_random_user_id()
        headers = {'Owner-Id': f'{current_user_id}'}
        response = self.client.post(
            url, data, format='multipart', headers=headers)
        self.assertEqual(response.status_code, 202)
        # assert photo exists
        photos = models.Photo.objects.all()
        self.assertEqual(len(photos), 1)
        self.assertEqual(photos[0].path, response.json()['path'])
        async_wrapper.assert_called_once()
        generate_presigned_url.assert_called_once()

    @patch('apiv1.tasks.generate_presigned_url')
    def test_get_photo_list(self, generate_presigned_url):
        """
        Test to validate that a get request to the API will return only photos
        where photo.owner_id = current_user_id.
        """
        current_user_id = self.get_random_user_id()
        # generate random entries that belong to current_user_id
        count, _ = self.generate_owner_fake_photo_entries(current_user_id)
        # generate random entries that do not belong to current_user_id
        other_count, _ = self.generate_random_fake_photo_entries(current_user_id)
        url = reverse('photo-list')
        # api needs owner_id information in order to fetch only owner photos.
        headers = {'Owner-Id': f'{current_user_id}'}
        response = self.client.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), count)
        calls_made = []
        for photo in models.Photo.objects.filter(owner_id=current_user_id):
            calls_made.append(call(photo.path))
        generate_presigned_url.assert_has_calls(calls_made, any_order=True)

    @patch('apiv1.tasks.generate_presigned_url')
    def test_get_photo_detail(self, generate_presigned_url):
        """
        Validate that a user of current_user_id == photo.owner_id can access
        a photo of photo.owner_id == current_user_id
        """
        current_user_id = self.get_random_user_id()
        _, photo_ids = self.generate_owner_fake_photo_entries(current_user_id)
        random_id = random.choice(photo_ids)
        random_photo = models.Photo.objects.get(pk=random_id)
        url = reverse('photo-detail', kwargs={'pk': random_id})
        headers = {'Owner-Id': current_user_id}
        response = self.client.get(url, headers=headers)
        generate_presigned_url.assert_called_once()
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(random_photo.path, data['path'])

    @patch('apiv1.tasks.generate_presigned_url')
    def test_put_photo(self, generate_presigned_url):
        current_user_id = self.get_random_user_id()
        _, photo_ids = self.generate_owner_fake_photo_entries(current_user_id)
        random_id = random.choice(photo_ids)
        random_photo = models.Photo.objects.get(pk=random_id)
        url = reverse('photo-detail', kwargs={'pk': random_id})
        new_data = {
            'image': self.get_uploaded_test_png()
        }
        headers = {'Owner-Id': current_user_id}
        response = self.client.put(url, new_data, headers=headers)
        generate_presigned_url.assert_called_once()
        data = response.json()
        self.assertEqual(response.status_code, 200)
        # fetch updated data from db
        random_photo.refresh_from_db()
        # old data updated to new data
        self.assertEqual(random_photo.path, data['path'])

    @patch('apiv1.tasks.async_delete_object_from_s3.delay')
    def test_delete_photo(self, async_delete_object_from_s3):
        current_user_id = self.get_random_user_id()
        count, photo_ids = self.generate_owner_fake_photo_entries(current_user_id)
        random_id = random.choice(photo_ids)
        random_photo = models.Photo.objects.get(pk=random_id)
        url = reverse('photo-detail', kwargs={'pk': random_id})
        headers = {'Owner-Id': current_user_id}
        response = self.client.delete(url, headers=headers)
        self.assertEqual(response.status_code, 204)
        photos = models.Photo.objects.all()
        self.assertEqual(count - 1, len(photos))
        async_delete_object_from_s3.assert_called_once_with(random_photo.path)
