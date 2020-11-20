import json
import logging
import os

import boto3
from botocore.exceptions import ClientError


def presigned_upload_url(request):
    S3_BUCKET = os.environ.get("S3_BUCKET")

    file_name = request.args.get("file_name")
    file_type = request.args.get("file_type")

    s3 = boto3.client("s3")

    presigned_post = s3.generate_presigned_post(
        Bucket=S3_BUCKET,
        Key=file_name,
        Fields={"acl": "public-read", "Content-Type": file_type},
        Conditions=[{"acl": "public-read"}, {"Content-Type": file_type}],
        ExpiresIn=3600,
    )

    return json.dumps(
        {
            "data": presigned_post,
            "url": "https://%s.s3.amazonaws.com/%s" % (S3_BUCKET, file_name),
        }
    )


def presigned_download_url(object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    bucket_name = os.environ.get("S3_BUCKET")
    # Generate a presigned URL for the S3 object
    s3_client = boto3.client("s3")
    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response
