import os
import sys
import io
import torch
from core.logs import logger
from fastapi import APIRouter
from fastapi import HTTPException
from schemas.schema import RequestReplace, ResponseV1
from diffusers import  StableDiffusionInpaintPipeline
from diffusers.pipelines.stable_diffusion import StableDiffusionSafetyChecker
from utils.helper import replace_anything_with_sd, read_images_from_s3, write_images_to_s3

router = APIRouter()

# prior = KandinskyV22PriorPipeline.from_pretrained("kandinsky-community/kandinsky-2-2-prior", torch_dtype=torch.float16)
# prior.to("cuda:2")
# kd_model = KandinskyV22InpaintPipeline.from_pretrained("kandinsky-community/kandinsky-2-2-decoder-inpaint", torch_dtype=torch.float16)
# kd_model.to("cuda:2")
# kd_model.enable_attention_slicing()
# kd_model.enable_model_cpu_offload()
sd_model = StableDiffusionInpaintPipeline.from_pretrained(
    "stabilityai/stable-diffusion-2-inpainting", torch_dtype=torch.float16,
    safety_checker=StableDiffusionSafetyChecker.from_pretrained(
        "CompVis/stable-diffusion-safety-checker",
        torch_dtype=torch.float16),
).to("cuda:2")    
sd_model.enable_xformers_memory_efficient_attention()


@router.post("/replace_anything")
async def replace_anything(request: RequestReplace):
    """
    Endpoint to generate images to replace anything behind the mask given an Image and text prompt

    Returns:
        ResponseV1: S3 URLs of generated images
        {
  "image_urls": [
        "https://vista-hackathon.s3.amazonaws.com/output_images/replace/RZK8D.jpg",
        "https://vista-hackathon.s3.amazonaws.com/output_images/replace/6AA5D.jpg",
        "https://vista-hackathon.s3.amazonaws.com/output_images/replace/DZ2HW.jpg",
        "https://vista-hackathon.s3.amazonaws.com/output_images/replace/HVSF5.jpg",
  ]
}
    """
    try:
        image_url, mask_url = request.image[0].get("image_url"), request.mask[0].get("mask_url")
        image, mask = read_images_from_s3(image_url), read_images_from_s3(mask_url, rgb=False)
        logger.info("Images loaded from S3 bucket!")

        images_response, folder = replace_anything_with_sd(sd_model, image, mask, request.text_prompt, request.negative_prompt)
        logger.info("Generated Images from Replace API")
        s3_paths = write_images_to_s3(images_response, api="replace", folder=folder)
        logger.info("Uploaded Images to S3 Bucket")
        return ResponseV1(**{"image_urls":s3_paths["image_urls"]})

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.error(f"Error e: {e}")
        print(exc_type, filename, exc_tb.tb_lineno)
        raise HTTPException(detail='Replace API Failed! Check your logs', status_code=500)
