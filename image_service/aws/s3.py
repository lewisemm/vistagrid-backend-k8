import os

import boto3


class S3Operations:
    def __init__(self):
        s3 = boto3.resource('s3')
        bucket_name = os.environ['S3_BUCKET']
        self.bucket = s3.Bucket(bucket_name)

    def upload_photo(self, binary_data, filename):
        self.bucket.put_object(Key=filename, Body=binary_data)
    
    def list_bucket_objects(self):
        count = 1
        for obj in self.bucket.objects.all():
            print(f'{count}. {obj.key}')
            count += 1

    def __repr__(self):
        return f'<S3Operations: {os.environ["S3_BUCKET"]}>'
