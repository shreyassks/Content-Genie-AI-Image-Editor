import json
import os
import sys
import boto3
import json

os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_PROFILE"] = "sso_profile"
os.environ["BEDROCK_ENDPOINT_URL"] = "https://bedrock.us-east-1.amazonaws.com"


modelId = 'anthropic.claude-instant-v1'
accept = 'application/json'
contentType = 'application/json'

boto3.setup_default_session(profile_name='sso_profile')

boto3_bedrock = boto3.client(service_name='bedrock',
                             region_name='us-east-1',
                             endpoint_url='https://bedrock.us-east-1.amazonaws.com')


def get_captions_using_bedrock(desc):
    prompt_for_caption = """Human: Generate 5 captions without hashtags for a social media post using the image description provided. \
    Make sure each caption is of different language. Choose languages from the mentioned list - [english, french, spanish, german, dutch]. \
    The post is for arbonne brand. Use the image description mentioned within the # symbol. Give response in json format with key as language . 

    ### Sample response ##
    {{"captions" : [{{
      "english": "Discover our new mascara. With a luxurious formula and precise brush",
      "french": "Découvrez notre nouveau",
      "spanish": "caption 3",
      "german": "Entdecken Sie unseren",
      "dutch": "luxe formule en precieze borstel"
    }}]
}}
####

Text : {}
Assistant: """

    complete_text = prompt_for_caption.format(desc)
    
    body = json.dumps({
        "prompt": complete_text,
        "max_tokens_to_sample":300,
        "temperature":1,
        "top_k":250,
        "top_p":0.999,
        "stop_sequences":["\\n\\nHuman:"],
        "anthropic_version":"bedrock-2023-05-31"
    })

    response = boto3_bedrock.invoke_model(body=body,
                                modelId=modelId, 
                                accept=accept, 
                                contentType=contentType)

    ai_response = json.loads(response.get('body').read())
    generated_resp = ai_response.get('completion').replace("\n","")
    caption_list = json.loads(generated_resp)["captions"][0]
    # generated_resp = generated_resp[generated_resp.index("\n\n")+1:]
    # generated_resp = generated_resp.replace("\n","")
    # caption_list = generated_resp.split("\n")
    # caption_list = [ x +" : "+y for x,y in zip(generated_resp.keys(), generated_resp.values())]
    return caption_list


def get_hashtags_using_bedrock(caption):
    prompt_for_hashtag = """Human: Generate a total of 5 hashtags for the mentioned caption for arbonne brand. \
    Atleast one hashtag should be related to the brand arbonne. Choose languages from the mentioned list - [english, french, spanish, german, dutch]. \
    The caption is mentioned as Text field. Give the response in JSON format with field key as hashtags.

### Sample response ##{{
  "hashtags": [
    "#One",
    "#two",
    "#Three",
    "#Four",
    "#Five"
  ]
}}
####

Text : {}

Assistant:
    """
    complete_text = prompt_for_hashtag.format(caption)
    
    body = json.dumps({
        "prompt": complete_text,
        "max_tokens_to_sample":300,
        "temperature":1,
        "top_k":250,
        "top_p":0.999,
        "stop_sequences":["\\n\\nHuman:"],
        "anthropic_version":"bedrock-2023-05-31"
    })

    response = boto3_bedrock.invoke_model(body=body,
                                modelId=modelId, 
                                accept=accept, 
                                contentType=contentType)

    ai_response = json.loads(response.get('body').read())
    generated_resp = ai_response.get('completion').replace("\n","")
    hashtag_list = json.loads(generated_resp)["hashtags"]

    # generated_resp = generated_resp[generated_resp.index('\n')+1:]
    # generated_resp = generated_resp['captions']
    # hashtag_list = generated_resp['hashtags']
    
    return hashtag_list


# if __name__=="__main__":
#     output_resp = get_captions_using_bedrock("a mascara tube and brush on a white surface with a black brush next to it and a black mascara")
#     print(output_resp)
#     output_resp = get_hashtags_using_bedrock(output_resp["english"])
#     print(output_resp)
