import torch
import requests
from PIL import Image
from transformers import AutoProcessor, Blip2ForConditionalGeneration

class ImageDescriptor:
    base_model = "Salesforce/blip2-opt-2.7b"
    processor = None
    model = None
    device = None

    def __init__(self):
        self.processor = AutoProcessor.from_pretrained(self.base_model)
        self.model = Blip2ForConditionalGeneration.from_pretrained(self.base_model,
                                                                   load_in_8bit=True)
        self.device = "cuda:3" if torch.cuda.is_available() else "cpu"

    def get_description(self, image):
        inputs = self.processor(images=image, return_tensors="pt").to(self.device, torch.float16)
        pixel_values = inputs.pixel_values
        generated_ids = self.model.generate(pixel_values=pixel_values, min_length=20, max_length=50)
        generated_caption = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return generated_caption

# if __name__=="__main__":
#     imageDescriptor=ImageDescriptor()
#     image_url = "https://flow-neo-dexter.s3.us-west-2.amazonaws.com/image-generation/dump-images/remove_sample.jpg"
#     image = Image.open(requests.get(image_url, stream=True).raw).convert('RGB')
#     desc=imageDescriptor.get_description(image)
#     print(desc)