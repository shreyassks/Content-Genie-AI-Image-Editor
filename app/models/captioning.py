import requests
from PIL import Image
import torch
from transformers import (
    T5ForConditionalGeneration,
    T5Tokenizer
)


class StylizedCaptionModel:

    caption_base_model = None
    stylized_caption_model = None
    tokenizer = None
    stylized_model = None

    device = "cuda" if torch.cuda.is_available() else "cpu"

    def __init__(self):
        self.caption_base_model = 't5-base'
        self.stylized_caption_model = "t5-base"
        self.tokenizer = T5Tokenizer.from_pretrained(self.caption_base_model, model_max_length=512, legacy=False)
        self.stylized_model = T5ForConditionalGeneration.from_pretrained(self.stylized_caption_model).to(self.device)

    def stylize_text(self, input_text, tokenizer, model, num_return_sequences):
        batch = tokenizer(input_text, truncation=True,
                          padding='max_length',
                          max_length=30,
                          return_tensors="pt").to(self.device)

        translated = model.generate(**batch,
                                    max_length=30,
                                    num_beams=4,
                                    num_return_sequences=num_return_sequences,
                                    temperature=1.5,
                                    top_k=50,
                                    top_p=0.95,
                                    use_cache=True,
                                    do_sample=True,
                                    early_stopping=True)

        tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
        return tgt_text

    def get_stylized_captions(self, description):
        captions=[]
        output = self.stylize_text([description],
                                     self.tokenizer,
                                     self.stylized_model, 3)
        
        for ele in output:
            temp = ele.replace("#", " #")
            ele = ' '.join(word for word in temp.split(' ') if not word.startswith('#'))
            captions.append(ele)
        print(captions)
        return captions


# if __name__=="__main__":
#     stylizedCaptionModel = StylizedCaptionModel()
#     desc = "a cup of tea sits on a desk next to a computer and a mouse pad with a note"
#     captions = stylizedCaptionModel.get_stylized_captions(desc)
    # print(captions)