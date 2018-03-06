from troposphere import Template
from troposphere.s3 import Bucket, VersioningConfiguration
from common import write_json_to_file
from s3.contacts_nplutt.config import resource_name, bucket_name


def create_s3_bucket(template=None):
    if not template:
        template = Template()
        template.add_description('This cloudformation template creates an s3 bucket for storing'
                                 'all of uploaded contact files.')
        template.add_version('2010-09-09')

    code_bucket = Bucket(
        resource_name,
        BucketName=bucket_name,
        VersioningConfiguration=VersioningConfiguration(
            Status='Enabled'
        )
    )

    template.add_resource(code_bucket)

    write_json_to_file('bucket.json', template)


if __name__ == '__main__':
    create_s3_bucket()
