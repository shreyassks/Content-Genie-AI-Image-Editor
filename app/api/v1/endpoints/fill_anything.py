import os
import sys
import torch
from fastapi import APIRouter
from core.logs import logger
from fastapi import HTTPException
from schemas.schema import RequestFill, ResponseV1
from diffusers import StableDiffusionInpaintPipeline
from diffusers.pipelines.stable_diffusion import StableDiffusionSafetyChecker
from utils.helper import fill_anything_with_sd, read_images_from_s3, write_images_to_s3

router = APIRouter()

sd_model = StableDiffusionInpaintPipeline.from_pretrained(
    "stabilityai/stable-diffusion-2-inpainting", torch_dtype=torch.float16,
    safety_checker=StableDiffusionSafetyChecker.from_pretrained(
        "CompVis/stable-diffusion-safety-checker",
        torch_dtype=torch.float16),
).to("cuda:1")    
sd_model.unet.load_attn_procs("artifacts/")
sd_model.enable_xformers_memory_efficient_attention()


@router.post("/fill_anything")
async def fill_anything(request: RequestFill):
    """
    Endpoint to generate images to fill anything behind the mask given an Image and text prompt

    Returns:
        ResponseV1: S3 URLs of generated images
        {
    "image_urls": [
        "https://vista-hackathon.s3.amazonaws.com/output_images/fill/RZK8D.jpg",
        "https://vista-hackathon.s3.amazonaws.com/output_images/fill/6AA5D.jpg",
        "https://vista-hackathon.s3.amazonaws.com/output_images/fill/DZ2HW.jpg",
        "https://vista-hackathon.s3.amazonaws.com/output_images/fill/HVSF5.jpg",
    ]
}
    """
    try:
        image_url, mask_url = request.image[0].get("image_url"), request.mask[0].get("mask_url")
        image, mask = read_images_from_s3(image_url), read_images_from_s3(mask_url, rgb=False)
        logger.info("Images loaded from S3 bucket!")

        images_response, folder = fill_anything_with_sd(sd_model, image, mask, request.text_prompt, request.negative_prompt)
        logger.info("Generated Images from Fill API")
        s3_paths = write_images_to_s3(images_response, api="fill", folder=folder)
        logger.info("Uploaded Images to S3 Bucket")
        return ResponseV1(**{"image_urls":s3_paths["image_urls"]})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(f"Error e: {e}")
        print(exc_type, filename, exc_tb.tb_lineno)
        raise HTTPException(detail='Fill API Failed! Check your logs', status_code=500)