import asyncio
import base64


from celery import shared_task


from aws import s3


async def async_upload_to_s3_wrapper(img, file_name):
    ## TODO: Use of img.chunks() is preferred.
    binary_data = img.read()
    encoded = base64.b64encode(binary_data).decode()
    async_upload_to_s3.delay(encoded, file_name)


@shared_task
def async_upload_to_s3(encoded, filename):
    decoded = base64.b64decode(encoded)
    sss = s3.S3Operations()
    sss.upload_photo(decoded, filename)
