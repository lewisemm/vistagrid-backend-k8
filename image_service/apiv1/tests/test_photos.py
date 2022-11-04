import os
import pathlib
import random

import faker
from django.conf import settings
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient


from apiv1 import models


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

    def generate_random_fake_photo_entries(self):
        # create fake entries
        count = int(random.random() * 10) + 1
        photo_ids = []
        for i in range(count):
            data = {
                'path': self.fake.file_name(),
                'owner_id': int(random.random() * 1000)
            }
            photo = models.Photo(**data)
            photo.save()
            photo_ids.append(photo.photo_id)
        return count, photo_ids

    def get_uploaded_test_png(self):
        photo = open(self.test_png_path, 'rb')
        photo = File(photo)
        photo = SimpleUploadedFile('uploaded.png', photo.read(), content_type='multipart/form-data')
        return photo

    def test_post_photo(self):
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
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        # assert photo exists
        photos = models.Photo.objects.all()
        self.assertEqual(len(photos), 1)
        self.assertEqual(photos[0].path, data['path'])

    def test_get_photo_list(self):
        count, _ = self.generate_random_fake_photo_entries()
        url = reverse('photo-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), count)

    def test_get_photo_detail(self):
        count, photo_ids = self.generate_random_fake_photo_entries()
        random_id = random.choice(photo_ids)
        random_photo = models.Photo.objects.get(pk=random_id)
        url = reverse('photo-detail', kwargs={'pk': random_id})
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(random_photo.path, data['path'])

    def test_put_photo(self):
        _, photo_ids = self.generate_random_fake_photo_entries()
        random_id = random.choice(photo_ids)
        random_photo = models.Photo.objects.get(pk=random_id)
        url = reverse('photo-detail', kwargs={'pk': random_id})
        new_data = {
            'image': self.get_uploaded_test_png()
        }
        # old data not equal to new (incoming) data
        print(f'old: {random_photo.path}, new: {new_data["path"]}')
        self.assertNotEqual(random_photo.path, new_data['path'])
        response = self.client.put(url, new_data, content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        # fetch updated data from db
        random_photo.refresh_from_db()
        # old data updated to new data
        self.assertEqual(random_photo.path, data['path'])

    def test_delete_photo(self):
        count, photo_ids = self.generate_random_fake_photo_entries()
        random_id = random.choice(photo_ids)
        random_photo = models.Photo.objects.get(pk=random_id)
        url = reverse('photo-detail', kwargs={'pk': random_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        photos = models.Photo.objects.all()
        self.assertEqual(count - 1, len(photos))
