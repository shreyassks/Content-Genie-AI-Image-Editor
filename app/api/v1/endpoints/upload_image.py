import os
import boto3
import random
import string
import base64
from PIL import Image
from io import BytesIO
from fastapi import APIRouter
from schemas.schema import UploadRequest
from botocore.exceptions import NoCredentialsError


router = APIRouter()


@router.post("/upload_image")
async def upload_image(request: UploadRequest):
    """
    Uploads the base64 image to S3 bucket
    :param base64_image:
    :param bucket_name:
    :return:
    """
    try:
        session = boto3.Session(profile_name='caredev-caredevleads')
        s3 = session.client('s3')

        bucket_name = request.bucket_name
        base64_image = request.base64_image
        # Decode the base64 image
        format_and_data = base64_image.split(";base64,")
        format = format_and_data[0][5:].split("/")[1]
        print(format)
        decoded_image = base64.b64decode(format_and_data[1])

        # Upload the decoded image to S3
        filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5)) + f".{format}"
        object_name = f"dump_images/{filename}"

        s3.upload_fileobj(BytesIO(decoded_image), bucket_name, object_name)

        # Generate the S3 URL for the uploaded object
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"

        return s3_url
    except NoCredentialsError:
        return "AWS credentials not available."
