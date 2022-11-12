import asyncio
import base64


from celery import shared_task


from aws import s3


async def async_upload_to_s3_wrapper(img, file_name, content_type):
    ## TODO: Use of img.chunks() is preferred.
    binary_data = img.read()
    encoded = base64.b64encode(binary_data).decode()
    async_upload_to_s3.delay(encoded, file_name, content_type)


@shared_task
def async_upload_to_s3(encoded, filename, content_type):
    decoded = base64.b64decode(encoded)
    sss = s3.S3Operations()
    sss.upload_photo(decoded, filename, content_type)


@shared_task
def async_delete_object_from_s3(object_key):
    sss = s3.S3Operations()
    sss.delete_bucket_object(object_key)
