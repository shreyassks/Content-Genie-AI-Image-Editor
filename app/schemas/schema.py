from typing import List
from enum import Enum
from pydantic import BaseModel


class RequestFill(BaseModel):
    image: List[dict] = [
        {"image_url": "https://vista-hackathon.s3.us-west-2.amazonaws.com/dump_images/fill_sample.png"}
    ]
    mask: List[dict] = [
        {"mask_url": "https://vista-hackathon.s3.us-west-2.amazonaws.com/dump_images/fill_mask.jpg"}
    ]
    text_prompt: str = "a photo of two body lotions, white colour, in focus, in foreground, extremely sharp"
    negative_prompt: str = "low quality, unrealistic, cartoon, low resolution, text"


class RequestReplace(BaseModel):
    image: List[dict] = [
        {"image_url": "https://vista-hackathon.s3.us-west-2.amazonaws.com/dump_images/replace_sample.jpg"}
    ]
    mask: List[dict] = [
        {"mask_url": "https://vista-hackathon.s3.us-west-2.amazonaws.com/dump_images/replace_mask.jpg"}
    ]
    text_prompt: str = "christmas themed decoration, colourful lighting"
    negative_prompt: str = "low quality, unrealistic, cartoon, low resolution"


class RequestRemove(BaseModel):
    image: List[dict] = [
        {"image_url": "https://vista-hackathon.s3.us-west-2.amazonaws.com/dump_images/remove_sample.jpg"}
    ]
    mask: List[dict] = [
        {"mask_url": "https://vista-hackathon.s3.us-west-2.amazonaws.com/dump_images/remove_mask.jpg"}
    ]


class ResponseV1(BaseModel):
    image_urls: List


class UploadRequest(BaseModel):
    base64_image: str
    bucket_name: str = "vista-hackathon"

class RequestCaption(BaseModel):
    image_url: str = "https://vista-hackathon.s3.us-west-2.amazonaws.com/dump_images/fill_sample.png"

class HDStrategy(str, Enum):
    # Use original image size
    ORIGINAL = "Original"
    # Resize the longer side of the image to a specific size(hd_strategy_resize_limit),
    # then do inpainting on the resized image. Finally, resize the inpainting result to the original size.
    # The area outside the mask will not lose quality.
    RESIZE = "Resize"
    # Crop masking area(with a margin controlled by hd_strategy_crop_margin) from the original image to do inpainting
    CROP = "Crop"


class Config(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    # Configs for High Resolution Strategy(different way to preprocess image)
    hd_strategy: str = HDStrategy.ORIGINAL  # See HDStrategy Enum
    hd_strategy_crop_margin: int = 128
    # If the longer side of the image is larger than this value, use crop strategy
    hd_strategy_crop_trigger_size: int = 128
    hd_strategy_resize_limit: int = 128
