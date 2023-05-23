import random
from unittest.mock import patch, call

import faker
from django.db import IntegrityError
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient


from apiv1 import models
from apiv1.tests.helpers import UtilityHelpers


class MockUserServiceResponse:
    """
    Mock response from the user_service.
    """
    def __init__(self):
        self.code = 200

    def readlines(self):
        return ['{"user_id": 2}'.encode('utf-8')]


class TestAPITransactions(TransactionTestCase, UtilityHelpers):
    def setUp(self):
        self.client = APIClient()

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

    @patch('apiv1.models.Photo.save', side_effect=IntegrityError)
    @patch('apiv1.tasks.async_upload_to_s3_wrapper')
    def test_post_photo_atomic_transaction_failure(
        self, async_wrapper, photo_save
    ):
        """
        Test photo create functionality when an error occurs within a
        transaction.
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
        self.assertEqual(response.status_code, 500)
        # assert photos still do not exist
        photos = models.Photo.objects.all()
        self.assertEqual(len(photos), 0)
        async_wrapper.assert_not_called()


class TestPhotos(APITestCase, UtilityHelpers):
    def setUp(self):
        self.client = APIClient()
        self.fake = faker.Faker()

    def tearDown(self):
        del self.client
        del self.fake

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
        headers = {'Owner-Id': f'{current_user_id}'}
        response = self.client.get(url, headers=headers)
        generate_presigned_url.assert_called_once()
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(random_photo.path, data['path'])

    @patch('apiv1.tasks.generate_presigned_url')
    def test_put_photo(self, generate_presigned_url):
        """
        Validate that a user of current_user_id == photo.owner_id can edit
        a photo of photo.owner_id == current_user_id
        """
        current_user_id = self.get_random_user_id()
        _, photo_ids = self.generate_owner_fake_photo_entries(current_user_id)
        random_id = random.choice(photo_ids)
        random_photo = models.Photo.objects.get(pk=random_id)
        url = reverse('photo-detail', kwargs={'pk': random_id})
        new_data = {
            'image': self.get_uploaded_test_png()
        }
        headers = {'Owner-Id': f'{current_user_id}'}
        response = self.client.put(url, new_data, headers=headers)
        generate_presigned_url.assert_called_once()
        data = response.json()
        self.assertEqual(response.status_code, 200)
        # fetch updated data from db
        random_photo.refresh_from_db()
        # old data updated to new data
        self.assertEqual(random_photo.path, data['path'])

    @patch('apiv1.tasks.async_delete_object_from_s3.s')
    def test_delete_photo(self, async_delete_object_from_s3):
        """
        Validate that a user of current_user_id == photo.owner_id can delete
        a photo of photo.owner_id == current_user_id
        """
        current_user_id = self.get_random_user_id()
        count, photo_ids = self.generate_owner_fake_photo_entries(current_user_id)
        random_id = random.choice(photo_ids)
        random_photo = models.Photo.objects.get(pk=random_id)
        url = reverse('photo-detail', kwargs={'pk': random_id})
        headers = {'Owner-Id': f'{current_user_id}'}
        response = self.client.delete(url, headers=headers)
        self.assertEqual(response.status_code, 204)
        photos = models.Photo.objects.all()
        self.assertEqual(count - 1, len(photos))
        async_delete_object_from_s3.assert_called_once_with(random_photo.path)

    def test_post_photo_no_owner_id_header(self):
        """
        Test the functionality to create photo entries when owner_id information
        is not passed via the "Owner-Id" header.
        """
        # no photos exist yet
        photos = models.Photo.objects.all()
        self.assertEqual(len(photos), 0)
        url = reverse('photo-list')
        data = {
            'image': self.get_uploaded_test_png()
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 401)
        # assert photo has not been created
        photos = models.Photo.objects.all()
        self.assertEqual(len(photos), 0)

    def test_post_photo_invalid_owner_id_header(self):
        """
        Test the functionality to create photo entries when "Owner-Id" header
        contains invalid value.
        Any value that cannot be converted to an int (to represent owner_id) is
        considered invalid.
        """
        # no photos exist yet
        photos = models.Photo.objects.all()
        self.assertEqual(len(photos), 0)
        url = reverse('photo-list')
        data = {
            'image': self.get_uploaded_test_png()
        }
        headers = {'Owner-Id': 'invalid header'}
        response = self.client.post(
            url, data, format='multipart', headers=headers)
        self.assertEqual(response.status_code, 401)
        # assert photo has not been created
        photos = models.Photo.objects.all()
        self.assertEqual(len(photos), 0)

    @patch('apiv1.tasks.generate_presigned_url')
    def test_get_photo_list_not_owner_photos(self, generate_presigned_url):
        """
        Test that user of `current_user_id` cannot list photos belonging to
        other users in the `photo-list` route.
        """
        current_user_id = self.get_random_user_id()
        # generate random entries that do not belong to current_user_id
        other_count, _ = self.generate_random_fake_photo_entries(current_user_id)
        url = reverse('photo-list')
        # assert that current_user_id has no photos
        photos = models.Photo.objects.filter(owner_id=current_user_id)
        self.assertEqual(len(photos), 0)
        headers = {'Owner-Id': f'{current_user_id}'}
        response = self.client.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 0)
        calls_made = []
        for photo in models.Photo.objects.filter(owner_id=current_user_id):
            calls_made.append(call(photo.path))
        generate_presigned_url.assert_has_calls(calls_made, any_order=True)
        # assert that photos from other users actually exist in the database
        photos = models.Photo.objects.exclude(owner_id=current_user_id)
        self.assertEqual(len(photos), other_count)

    @patch('apiv1.tasks.generate_presigned_url')
    def test_get_photo_detail_not_owner_photos(self, generate_presigned_url):
        """
        Test that user of `current_user_id` cannot access photo details of photo
        belonging to other user in `photo-detail` route.
        """
        current_user_id = self.get_random_user_id()
        other_count, photo_ids = self.generate_random_fake_photo_entries(
            current_user_id)
        random_id = random.choice(photo_ids)
        random_photo = models.Photo.objects.get(pk=random_id)
        url = reverse('photo-detail', kwargs={'pk': random_id})
        headers = {'Owner-Id': f'{current_user_id}'}
        response = self.client.get(url, headers=headers)
        self.assertEqual(response.status_code, 403)
        generate_presigned_url.assert_not_called()

    @patch('apiv1.tasks.generate_presigned_url')
    def test_put_photo_not_owner_photos(self, generate_presigned_url):
        """
        Test that user of `current_user_id` cannot edit photo details of photo
        belonging to other user in `photo-detail` route.
        """
        current_user_id = self.get_random_user_id()
        count, photo_ids = self.generate_random_fake_photo_entries(current_user_id)
        # assert photos exist
        photos = models.Photo.objects.all()
        self.assertEqual(len(photos), count)
        # assert current_user_id has no photos
        photos = photos.filter(owner_id=current_user_id)
        self.assertEqual(len(photos), 0)
        random_id = random.choice(photo_ids)
        random_photo = models.Photo.objects.get(pk=random_id)
        url = reverse('photo-detail', kwargs={'pk': random_id})
        new_data = {
            'image': self.get_uploaded_test_png()
        }
        headers = {'Owner-Id': f'{current_user_id}'}
        response = self.client.put(url, new_data, headers=headers)
        generate_presigned_url.assert_not_called()
        data = response.json()
        self.assertEqual(response.status_code, 403)

    @patch('apiv1.tasks.async_delete_object_from_s3.delay')
    def test_delete_photo_not_owner_photos(self, async_delete_object_from_s3):
        """
        Test that user of `current_user_id` cannot delete photo belonging to
        other user in `photo-detail` route.
        """
        current_user_id = self.get_random_user_id()
        count, photo_ids = self.generate_random_fake_photo_entries(current_user_id)
        random_id = random.choice(photo_ids)
        random_photo = models.Photo.objects.get(pk=random_id)
        url = reverse('photo-detail', kwargs={'pk': random_id})
        headers = {'Owner-Id': f'{current_user_id}'}
        response = self.client.delete(url, headers=headers)
        self.assertEqual(response.status_code, 403)
        # assert photo not deleted
        # if no exception is raised, the photo exists
        photo = models.Photo.objects.get(pk=random_id)
        self.assertIsNotNone(photo)
        self.assertEqual(photo, random_photo)
        async_delete_object_from_s3.assert_not_called()
