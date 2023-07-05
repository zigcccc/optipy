import boto3

from optipy.config import settings


s3 = boto3.client(
    "s3",
    endpoint_url=settings.AWS_URL,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION_NAME
)
