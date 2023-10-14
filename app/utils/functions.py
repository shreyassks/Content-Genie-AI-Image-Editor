import logging
from PIL import Image
import requests
from models.descriptor import ImageDescriptor
from models.captioning import StylizedCaptionModel
from utils.bedrock_helper import get_captions_using_bedrock, get_hashtags_using_bedrock


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

imageDescriptor = ImageDescriptor()
# stylizedCaptionModel = StylizedCaptionModel()

def get_description(image: Image):
    """
        Function to return description for the image sent as parameter using blip2 model
        :param image: Image type
        :return: String
    """
    desc = imageDescriptor.get_description(image)
    return desc

def get_captions(description):
    """
        Function to generate multiple stylized captions based on the image description using claudia
        :param description: string : Image description
        :return: : list of stylized captions
    """
    captions = stylizedCaptionModel.get_stylized_captions(description)
    return captions

def bedrock_captions(description):
    """
        Function to generate multiple stylized captions based on the image description using claudia
        :param description: string : Image description
        :return: : list of stylized captions
    """
    captions = get_captions_using_bedrock(description)
    return captions

def get_hashtags(description):
    """
        Function to generate top 5 hashtags based on the image description using claudia
        :param description: string : Image description
        :return: : list of hashtags
        """
    hashtags = get_hashtags_using_bedrock(description)
    return hashtags

# if __name__=="__main__":
#     # stylizedCaptionModel=StylizedCaptionModel()
#     image_url = "https://www.instagram.com/p/BdfXT_Onnge/media/?size=l"
#     image = Image.open(requests.get(image_url, stream=True).raw).convert('RGB')
#     captions=get_description(image)

