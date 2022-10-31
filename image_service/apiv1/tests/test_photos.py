import random

import faker
from django.test import Client, TestCase
from django.urls import reverse

from apiv1 import models

class TestPhotos(TestCase):
    def setUp(self):
        self.client = Client()
        self.fake = faker.Faker()

    def tearDown(self):
        del self.client
        del self.fake

    def test_post_photo(self):
        """
        Test photo create functionality.
        """
        # no photos exist yet
        photos = models.Photo.objects.all()
        self.assertEqual(len(photos), 0)
        url = reverse('photo-list')
        data = {
            'path': self.fake.file_name()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        # assert photo exists
        photos = models.Photo.objects.all()
        self.assertEqual(len(photos), 1)
        self.assertEqual(photos[0].path, data['path'])

    def test_get_photo_list(self):
        # create fake entries
        count = int(random.random() * 10)
        for i in range(count):
            data = {
                'path': self.fake.file_name(),
                'owner_id': int(random.random() * 1000)
            }
            models.Photo(**data).save()
        url = reverse('photo-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), count)
