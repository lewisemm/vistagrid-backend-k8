from django.db import models

from apiv1 import tasks

# Create your models here.
class Photo(models.Model):
    photo_id = models.BigAutoField(primary_key=True)
    path = models.CharField(max_length=255)
    owner_id = models.PositiveBigIntegerField()


    def get_signed_url(self):
        return tasks.generate_presigned_url(self.path)

    def __repr__(self):
        return f'<Photo: {self.photo_id}>'
