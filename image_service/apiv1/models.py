from django.db import models

# Create your models here.
class Photo(models.Model):
    photo_id = models.BigAutoField(primary_key=True)
    path = models.CharField(max_length=255)
    owner_id = models.PositiveBigIntegerField()

    def __repr__(self):
        return f'<Photo: {self.photo_id}>'
