from abc import ABC
import os
import sys
import cv2
import numpy as np
import torch

from utils.lama_helper import (
    norm_img,
    load_jit_model,
)
from models.base import InpaintModel
from schemas.schema import Config


class Lama(InpaintModel, ABC):
    name = "lama"
    pad_mod = 8

    def init_model(self, device, **kwargs):
        self.model = load_jit_model("artifacts/big-lama.pt", device).eval()

    def forward(self, image, mask, config: Config):
        """Input image and output image have same size
        image: [H, W, C] RGB
        mask: [H, W]
        return: BGR IMAGE
        """
        try:
            image = norm_img(image)
            mask = norm_img(mask)

            mask = (mask > 0) * 1
            image = torch.from_numpy(image).unsqueeze(0).to(self.device)
            mask = torch.from_numpy(mask).unsqueeze(0).to(self.device)

            inpainted_image = self.model(image, mask)

            cur_res = inpainted_image[0].permute(1, 2, 0).detach().cpu().numpy()
            cur_res = np.clip(cur_res * 255, 0, 255).astype("uint8")
            cur_res = cv2.cvtColor(cur_res, cv2.COLOR_RGB2BGR)
            return cur_res
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Error e: {e}")
            print(exc_type, filename, exc_tb.tb_lineno)
