import os

import boto3


class S3Operations:
    def __init__(self):
        self.s3_resource = boto3.resource('s3')
        bucket_name = os.environ['S3_BUCKET']
        self.bucket = self.s3_resource.Bucket(bucket_name)

    def upload_photo(self, binary_data, filename, content_type=None):
        metadata = {}
        if content_type:
            metadata['Content-Type'] =  content_type
        self.bucket.put_object(Key=filename, Body=binary_data, Metadata=metadata)
    
    def list_bucket_objects(self):
        count = 1
        for obj in self.bucket.objects.all():
            print(f'{count}. {obj.key}')
            count += 1

    def delete_bucket_object(self, object_key):
        bucket_name = os.environ['S3_BUCKET']
        s3_object = self.s3_resource.Object(bucket_name, object_key)
        s3_object.delete()

    def __repr__(self):
        return f'<S3Operations: {os.environ["S3_BUCKET"]}>'
