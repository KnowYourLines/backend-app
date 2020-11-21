import logging
import os

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


def presigned_upload_url(file_name):
    S3_BUCKET = os.environ.get("S3_BUCKET")

    s3 = boto3.client(
        "s3", config=Config(region_name="eu-west-2", signature_version="s3v4")
    )

    presigned_post = s3.generate_presigned_post(
        Bucket=S3_BUCKET,
        Key=file_name,
        Fields={"acl": "public-read", "Content-Type": "audio/wav"},
        Conditions=[{"acl": "public-read"}, {"Content-Type": "audio/wav"}],
        ExpiresIn=3600,
    )

    return {
        "data": presigned_post,
        "url": "https://%s.s3.amazonaws.com/%s" % (S3_BUCKET, file_name),
    }


def presigned_download_url(object_name, expiration=604800):
    """Generate a presigned URL to share an S3 object

    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    bucket_name = os.environ.get("S3_BUCKET")
    # Generate a presigned URL for the S3 object
    s3_client = boto3.client(
        "s3", config=Config(region_name="eu-west-2", signature_version="s3v4")
    )
    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
    except ClientError as e:
        logging.error(e)
        return None

    return url
