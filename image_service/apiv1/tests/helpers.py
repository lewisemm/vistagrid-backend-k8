import random
import os
import pathlib

from django.conf import settings
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile

from apiv1 import models


class UtilityHelpers:
    def get_uploaded_test_png(self):
        test_png_relative_path = pathlib.Path('apiv1/tests/uploadable/test.png')
        self.test_png_path = os.path.join(
            settings.BASE_DIR.parent,
            test_png_relative_path
        )
        photo = open(self.test_png_path, 'rb')
        photo = File(photo)
        photo = SimpleUploadedFile(
            'uploaded.png', photo.read(), content_type='multipart/form-data')
        return photo

    def get_random_user_id(self):
        """
        Generates and returns a random user_id that falls between 1 - 1000.
        """
        return int(random.random() * 1000)

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
