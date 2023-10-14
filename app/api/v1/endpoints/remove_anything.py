import os
import sys
import io

from fastapi import APIRouter
from schemas.schema import RequestRemove, ResponseV1
from utils.helper import remove_anything_with_lama, read_images_from_s3, write_images_to_s3

router = APIRouter()


@router.post("/remove_anything")
async def remove_anything(request: RequestRemove):
    """
    Endpoint to generate images to remove anything behind the mask given an Image and text prompt

    Returns:
        ResponseV1: S3 URLs of generated images
        {
  "image_urls": [
    "https://flow-neo-dexter.s3.amazonaws.com/image-generation/output_images/remove/1GTSU.jpg"
  ]
}
    """
    try:
        image_url, mask_url = request.image[0].get("image_url"), request.mask[0].get("mask_url")
        image, mask = read_images_from_s3(image_url), read_images_from_s3(mask_url, rgb=False)

        images_response, folder = remove_anything_with_lama(image, mask)
        s3_paths = write_images_to_s3(images_response, api="remove", folder=folder)
        return ResponseV1(**{"image_urls":s3_paths["image_urls"]})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error e: {e}")
        print(exc_type, filename, exc_tb.tb_lineno)