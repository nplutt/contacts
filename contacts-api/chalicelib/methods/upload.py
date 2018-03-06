import boto3
import logging

from os import getenv, remove
from chalice import BadRequestError, ChaliceViewError, Response
from uuid import uuid4


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BUCKET = getenv("BUCKET_NAME")
s3 = boto3.client("s3")


def upload_file(raw_body):
    """
    Writes the file to /tmp/, uploads the file to S3, and deletes the
    file from /tmp/
    Args:
        raw_body ()
    """
    if not raw_body:
        logger.warning("Received empty raw body, bad request.")
        raise BadRequestError

    file_name = "{}.csv".format(str(uuid4()))
    file_path = "/tmp/{}".format(file_name)

    try:
        logger.info("Writing file to {}...".format(file_path))
        with open(file_path, 'wb') as tmp_file:
            tmp_file.write(raw_body)

        logger.info("Uploading file {} to s3 bucket...".format(file_name))
        s3.upload_file(file_path, BUCKET, file_name)

    except Exception as e:
        logger.critical("Something went wrong when uploading file to s3."
                        "Received error message of: {}".format(e))
        raise ChaliceViewError

    finally:
        logger.info("Removing file {} from tmp".format(file_name))
        remove(file_path)

    logger.info("File successfully uploaded to S3")
    return Response(body=None,
                    status_code=201,
                    headers=dict())
