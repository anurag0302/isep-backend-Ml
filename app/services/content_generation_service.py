from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from huggingface_hub import InferenceClient
from app.utils.constants import MixtralConfig
from app.utils.config import HUGGINGFACE_TOKEN




processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

client = InferenceClient("mistralai/Mixtral-8x7B-Instruct-v0.1",token=HUGGINGFACE_TOKEN)


def generate_img_desc(image: Image.Image):
    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)

def generate_mixtral_content(prompt, retry=True):
    try:
        temperature = float(MixtralConfig.TEMPERATURE)
        if temperature < 1e-2:
            temperature = 1e-2
        top_p = float(MixtralConfig.TOP_P)

        generate_kwargs = dict(
            temperature=MixtralConfig.TEMPERATURE,
            max_new_tokens=MixtralConfig.MAX_NEW_TOKEN,
            top_p=top_p,
            repetition_penalty=MixtralConfig.REPETITION_PENALTY,
            do_sample=True,
            seed=42,
        )
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"
        stream = client.text_generation(formatted_prompt, **generate_kwargs, stream=True, details=True, return_full_text=False)
        output = ""
        for response in stream:
            output += response.token.text
        return output
    except Exception as e:
        print(f"An error occurred: {e}")
        if retry:
            return generate_mixtral_content(prompt, retry=False)  # Recursive call with retry=False
        return None

        

def format_caption_text(text):
    text_phrases = text.split('\n')
    text_phrases = list(filter(None, text_phrases))
    processed_phrases = [phrase.split('. "')[1][:-1] for phrase in text_phrases]
    return processed_phrases

def extract_caption_values(generated_captions_response):
    return [val.strip() for val in re.findall(r'"([^"]*)"', generated_captions_response)]



def format_caption_text_product(text):
    text_lines = text.split('\n')
    processed_lines = []
    for line in text_lines:
        # Split each line based on the first occurrence of ". " and remove leading numbers
        parts = line.split('. ', 1)
        if len(parts) > 1:
            processed_lines.append(parts[1])
    return processed_lines

def format_hashtags_text(text):
    text_phrases = text.split('\n')
    text_phrases = list(filter(None, text_phrases))
    processed_phrases = []
    for phrase in text_phrases:
        parts = phrase.split('. ')
        if len(parts) > 1:
            processed_phrases.append(parts[1])
    
    return processed_phrases

import re

def extract_hashtags(text):
    hashtags = re.findall(r'#\w+', text)
    return hashtags

def remove_s_tag(text):
    if "</s>" in text:
        text = text.replace("</s>", "")
    return text

def remove_hashtags(strings):
    return [re.sub(r'#\w+', '', s) for s in strings]


def extract_filter_values_array(categories_string):
    categories = re.findall(r"'([^']*)'", categories_string)
    return categories