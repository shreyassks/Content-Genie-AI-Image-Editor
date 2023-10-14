from fastapi import APIRouter
import logging
from utils.functions import get_description, get_hashtags, bedrock_captions
from utils.helper import read_images_from_s3
from fastapi import HTTPException
from schemas.schema import RequestCaption
import time


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()


@router.post("/get_captions")
async def get_captions(request_obj: RequestCaption):
    """
    Endpoint to generate images captions and hashtags

    Returns:
        dict of captions and hashtags: Generated Images
    """
    image_url = request_obj.image_url
    if image_url is None or image_url == "":
        raise HTTPException(detail='Image url received empty!', status_code=500)

    try:
        image = read_images_from_s3(image_url)
        logger.info(f'Reading the final image saved in S3 for captioning')
    except Exception as e:
        logger.error(f'Image reading from s3 failed  - {e}')
        raise HTTPException(detail=f'Image reading from s3 failed! {e}', status_code=500)
    
    try:
        description = get_description(image)
        caption_1 = bedrock_captions(description)
        final_caption = [ x +" : "+y for x,y in zip(caption_1.keys(), caption_1.values())]
    
    except Exception as e:
        logger.error(f'Caption generation failed  - {e}')
        raise HTTPException(detail=f'Caption generation failed! {e}', status_code=500)

    try:
        hashtags = get_hashtags(caption_1["english"])
    except Exception as e:
        logger.error(f'Hashtags generation failed  - {e}')
        raise HTTPException(detail=f'Hashtags generation failed! {e}', status_code=500)

    return {"captions": final_caption,
            "hashtags": hashtags}
