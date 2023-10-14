import os
import io
import sys
import torch
import numpy as np

import cv2
import boto3
import random
import string
import requests
from typing import List
from core.logs import logger

from PIL import Image, ImageFilter
from models.lama import Lama
from schemas.schema import Config
from diffusers import AutoPipelineForInpainting


def prepare_mask(img: Image, mask: Image, mask_invert=False, mask_blur: int = 20):
    try:
        img = np.asarray(img)
        if mask_invert:
            dummy_ones = np.ones((img.shape[0], img.shape[1]), dtype=np.float32)
            mask_norm = dummy_ones - np.asarray(mask.convert("L")) / 255.
            mask_img = Image.fromarray(np.uint8(mask_norm) * 255).convert("L")
        else:
            mask_img = mask.convert("L")

        mask_img = mask_img.filter(ImageFilter.GaussianBlur(mask_blur))
        return img, mask_img

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error e: {e}")
        print(exc_type, filename, exc_tb.tb_lineno)


def replace_anything_with_sd(
        model,
        # prior,
        img: Image,
        mask: Image,
        text_prompt: str,
        negative_prompt: str,
        steps: int = 50,
        height: int = 512,
        width: int = 512,
        guidance_scale: float = 9.5,
        generator: int = 42,
):
    """
    Replaces the background based on provided text prompt with a newly generated image
    :param img: input image
    :param mask: masked (B/W) image
    :param text_prompt: text description of the background to be replaced
    :param steps: number of inference steps
    :param width: width of generated image
    :param height: height of generated image
    :param generator: random number generator
    :param guidance_scale: importance given to the text prompt while image generation
    :return: 4 generated images
    """
    try:
        image, mask_image = prepare_mask(img, mask, mask_invert=True)
        # image_emb, zero_image_emb = prior(text_prompt, negative_prompt, return_dict=False)

        images = model(
            image=image,
            mask_image=mask_image,
            prompt=text_prompt,
            negative_prompt=negative_prompt,
            height=height,
            width=width,
            # image_embeds=image_emb,
            # negative_image_embeds=zero_image_emb,
            num_inference_steps=steps,
            num_images_per_prompt=4,
            generator=torch.Generator().manual_seed(generator)
        ).images
        # saving images to assets folder
        folder_path = "assets/replace"
        image_names = []
        for idx, img in enumerate(images):
            name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5)) + ".jpg"
            img.save(f"{folder_path}/{name}")
            image_names.append(name)
        return image_names, folder_path

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error e: {e}")
        print(exc_type, filename, exc_tb.tb_lineno)


def fill_anything_with_sd(
        model,
        img: Image,
        mask: Image,
        text_prompt: str,
        negative_prompt: str,
        steps: int = 50,
        height: int = 512,
        width: int = 512,
        guidance_scale: float = 9.5,
        generator: int = 42,
):
    """
    Replaces the masked portion based on provided text prompt with a newly generated fill
    :param img: input image
    :param mask: masked (B/W) image
    :param text_prompt: text description of the fill to be replaced
    :param negative_prompt: objects not to be generated
    :param steps: number of inference steps
    :param width: width of generated image
    :param height: height of generated image
    :param generator: random number generator
    :param guidance_scale: importance given to the text prompt while image generation
    :param device: CPU/CUDA
    :return: 4 generated images
    """
    try:
        image, mask_image = prepare_mask(img, mask)
        img_filled = model(
            prompt=text_prompt,
            negative_prompt=negative_prompt,
            image=Image.fromarray(image),
            mask_image=mask_image,
            num_inference_steps=steps,
            height=height,
            width=width,
            guidance_scale=guidance_scale,
            num_images_per_prompt=4,
            generator=torch.Generator().manual_seed(generator),
        ).images

        # saving images to assets folder
        folder_path = "assets/fill"
        image_names = []
        for idx, img in enumerate(img_filled):
            name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5)) + ".jpg"
            img.save(f"{folder_path}/{name}")
            image_names.append(name)
        return image_names, folder_path

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error e: {e}")
        print(exc_type, filename, exc_tb.tb_lineno)


def remove_anything_with_lama(
        img: Image,
        mask: Image,
        device="cuda"
):
    """
    Replaces the masked portion based on provided text prompt with a newly generated fill
    :param img: input image
    :param mask: masked (B/W) image
    :param device: CPU/CUDA
    :return: 1 generated images
    """
    try:
        config = Config()
        model_init = Lama(device=device)
        img, mask = np.asarray(img), np.asarray(mask.convert("L"))
        image = model_init(img, mask, config)
        res_img = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_BGR2RGB)

        # saving images to assets folder
        folder_path = "assets/remove"
        name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5)) + ".jpg"
        img = Image.fromarray(res_img)
        img.save(f"{folder_path}/{name}")
        return [name], folder_path

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error e: {e}")
        print(exc_type, filename, exc_tb.tb_lineno)


def read_images_from_s3(image_url, rgb=True):
    try:
        r = requests.get(image_url, stream=True)
        if rgb:    
            image = Image.open(io.BytesIO(r.content)).convert("RGB").resize((512, 512))
        else:
            image = Image.open(io.BytesIO(r.content)).convert("L").resize((512, 512))
        return image

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error e: {e}")
        print(exc_type, filename, exc_tb.tb_lineno)


def write_images_to_s3(image_name, api, folder="assets", bucket_name="vista-hackathon"):
    image_paths = []
    session = boto3.Session(profile_name='caredev-caredevleads')
    s3 = session.resource('s3')

    for filename in image_name:
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            image_path = os.path.join(folder, filename)
            s3_object_key = f"output_images/{api}/{filename}"
            s3.Bucket(bucket_name).upload_file(image_path, s3_object_key)
            s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_object_key}"
            image_paths.append(s3_url)
            logger.info(f"Uploaded {filename} to S3")

    response = create_response(image_paths)
    return response


def create_response(images: List):
    """Creates a complete Response object from given parameters
        Args:
            images: Image URL

        Returns:
            Response: a class object of Response
        """
    response = {"image_urls": images}
    return response
