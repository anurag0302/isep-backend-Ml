from fastapi import APIRouter, UploadFile, File
from ..services.content_generation_service import generate_img_desc, generate_mixtral_content, format_caption_text_product, extract_caption_values, remove_s_tag, remove_hashtags, extract_filter_values_array
from PIL import Image
from app.models.content_generation import SuccessObjectsResponse, SuccessHashtagsResponse, SuccessCaptionsResponse, CaptionGenerationRequest, hashtagsGenerationRequest,GenerateDescriptionCaption, FilterGenerationRequest, ToneGenerationRequest
from app.utils.helper import CustomErrorResponse
from app.utils.constants import ResponseValues
import re
from typing import Optional



router = APIRouter()

@router.post("/objects-detection", response_model=SuccessObjectsResponse)
async def image_caption(file: UploadFile = File(...)):
    try:
        if file is None:
            return CustomErrorResponse.generate_response("Empty Input", "File cannot be empty", 404)    
        if file.filename == "":
            return CustomErrorResponse.generate_response("Invalid Input", "File name cannot be empty", 400)
        img = Image.open(file.file).convert("RGB")
        image_description = generate_img_desc(img)
        
        prompt = "give me objects separated by commas from this sentence with no explanations only words :"+ image_description
        mixtral_prompt_objects = generate_mixtral_content(prompt)
        if '\n' in mixtral_prompt_objects:
            output_list = mixtral_prompt_objects.split("\n")
        elif '</s' in mixtral_prompt_objects:
            output_list = mixtral_prompt_objects.split("</s")
        else:
            output_list = mixtral_prompt_objects.split(".")
            
        output_list = output_list[0].split(", ")
        response= {
            "objects": output_list,
            "image_description":image_description
            }
        
        return {"status": ResponseValues.SUCCESS, "message": "objects generated successfully", "body": response}
    except Exception as e:        
        return CustomErrorResponse.generate_response("Error", str(e), 500)
    
    
    
@router.post("/generate-captions", response_model=SuccessCaptionsResponse)
async def generate_captions(data: CaptionGenerationRequest):
    try:
        objects = data.objects
        image_description = data.image_description
        filters=data.filters
        if not objects:
            return CustomErrorResponse.generate_response("Error", "Objects are Empty", 404)
        elif not image_description:
            return CustomErrorResponse.generate_response("Error", "Image Description is Empty", 404)
        
        prompt = "make similar sentence like this :"+ image_description+"from these words"+ ", ".join(objects)
        generated_new_description = generate_mixtral_content(prompt)
        
        prompt = "give me 10 social media caption for this without hastags:"+ generated_new_description
        
        if filters is not None:
            if filters.mood:
                prompt += " add " + filters.mood + " mood"
            if filters.category:
                prompt += " add " + ", ".join(filters.category) + " in category"
            if filters.tone:
                prompt += " with " + filters.tone + " tone"
            if filters.app:
                prompt += " for " + ", ".join(filters.app) + " apps"
            if filters.length:
                if filters.length == "Short":
                    prompt += " in 10 words each."
                elif filters.length == "Descriptive":
                    prompt += " in 50 words each."

        generated_captions_response = generate_mixtral_content(prompt)

        formated_captions_response= extract_caption_values(generated_captions_response)
                    
        formated_captions_response=formated_captions_response[:-1]
        
        if filters:
            if filters.sort == "Length":
                formated_captions_response=sorted(formated_captions_response, key=lambda x: len(x))
                
        captions_response={
            "captions": remove_hashtags(formated_captions_response)
        }
        response={
            "status": ResponseValues.SUCCESS,
            "message": "captions generated successfully",
            "body": captions_response
            }
        return response
    
    except Exception as e:        
        return CustomErrorResponse.generate_response("Error", str(e), 500)
         
 

@router.post("/generate-hashtags", response_model=SuccessHashtagsResponse)
async def generate_hashtags(data: hashtagsGenerationRequest):
    try:
        objects = data.objects
        image_description = data.image_description
        filters=data.filters
        
        if not objects:
            return CustomErrorResponse.generate_response("Error", "Objects are Empty", 404)
        elif not image_description:
            return CustomErrorResponse.generate_response("Error", "Image Description is Empty", 404)
        
        prompt = "make similar sentence like this :"+ image_description+"from these words"+ ", ".join(objects)
        generated_new_description = generate_mixtral_content(prompt)
        
        prompt = "give me 30 social media hashtags for this:"+ generated_new_description
        
        if filters is not None:
            if filters.mood:
                prompt += " add " + filters.mood + " mood"
            if filters.category:
                prompt += " add " + ", ".join(filters.category) + " in category"
            if filters.tone:
                prompt += " with " + filters.tone + " tone"
            if filters.app:
                prompt += " for " + ", ".join(filters.app) + " apps"
            
             
        generated_hashtags_response = generate_mixtral_content(prompt)
        
        formated_hashtags_response = re.findall(r'#\w+', generated_hashtags_response)
        
        if filters:
            if filters.sort == "Length":
                formated_hashtags_response=sorted(formated_hashtags_response, key=lambda x: len(x))

        hashtags_response={
            "hashtags": formated_hashtags_response
        }
        response={
            "status": ResponseValues.SUCCESS,
            "message": "Hashtags generated successfully",
            "body": hashtags_response
            }
        return response
    
    except Exception as e:        
        return CustomErrorResponse.generate_response("Error", str(e), 500)
    


@router.post("/text-description/generate-captions",response_model=SuccessCaptionsResponse)
async def generate_desc_captions(data: GenerateDescriptionCaption):
    try:
        required_fields = {
            "description": data.description,
        }

        for field_name, field_value in required_fields.items():
            if not field_value:
                error_message = f"{field_name} not provided"
                return CustomErrorResponse.generate_response(error_message, "Error", 400)
        filters=data.filters
        
            
        prompt = "give me 10 social media caption with this input"+  data.description+" without hastag."
        
        if filters is not None:
            if filters.mood:
                prompt += " add " + filters.mood + " mood"
            if filters.category:
                prompt += " add " + ", ".join(filters.category) + " in category"
            if filters.tone:
                prompt += " with " + filters.tone + " tone"
            if filters.app:
                prompt += " for " + ", ".join(filters.app) + " apps"
            if filters.length:
                if filters.length == "Short":
                    prompt += " in 10 words each."
                elif filters.length == "Descriptive":
                    prompt += " in 50 words each."
                    
        generated_captions_response = generate_mixtral_content(prompt)
        
        formated_captions_response= extract_caption_values(generated_captions_response)
    
        formated_captions_response=formated_captions_response[:-1]
        
        if filters:
            if filters.sort == "Length":
                formated_captions_response=sorted(formated_captions_response, key=lambda x: len(x))
                
        captions_response={
            "captions": remove_hashtags(formated_captions_response)
        }
        response={
            "status": ResponseValues.SUCCESS,
            "message": "captions generated successfully",
            "body": captions_response
            }
        return response
    
    except Exception as e:        
        return CustomErrorResponse.generate_response("Error", str(e), 500)
         
@router.post("/text-description/generate-hashtags", response_model=SuccessHashtagsResponse)
async def generate_desc_hashtags(data: GenerateDescriptionCaption):
    try:
        required_fields = {
            "description": data.description,
        }
        filters=data.filters
        

        for field_name, field_value in required_fields.items():
            if not field_value:
                error_message = f"{field_name} not provided"
                return CustomErrorResponse.generate_response(error_message, "Error", 400)
            
        prompt = "give me 20 social media hashtags for this:"+ data.description
        
        
        if filters is not None:
            if filters.mood:
                prompt += " add " + filters.mood + " mood"
            if filters.category:
                prompt += " add " + ", ".join(filters.category) + " in category"
            if filters.tone:
                prompt += " with " + filters.tone + " tone"
            if filters.app:
                prompt += " for " + ", ".join(filters.app) + " apps"
                
        generated_hashtags_response = generate_mixtral_content(prompt)

        formated_hashtags_response = re.findall(r'#\w+', generated_hashtags_response)

        if filters:
            if filters.sort == "Length":
                formated_hashtags_response=sorted(formated_hashtags_response, key=lambda x: len(x))
             
        
        hashtags_response={
            "hashtags": formated_hashtags_response
        }
        response={
            "status": ResponseValues.SUCCESS,
            "message": "Hashtags generated successfully",
            "body": hashtags_response
            }
        return response
    
    except Exception as e:        
        return CustomErrorResponse.generate_response("Error", str(e), 500)


@router.post("/product-description")
async def generate_product_desc(data: CaptionGenerationRequest):
    try:
        objects = data.objects
        image_description = data.image_description
        if not objects:
            return CustomErrorResponse.generate_response("Error", "Objects are Empty", 404)
        elif not image_description:
            return CustomErrorResponse.generate_response("Error", "Image Description is Empty", 404)
        
        prompt = "make similar sentence like this :"+ image_description+"from these words"+ ", ".join(objects)
        generated_new_description = generate_mixtral_content(prompt)
        
        prompt = "give me 5 products description for this with hastags:"+ generated_new_description+"each description in 100 words"
        generated_captions_response = generate_mixtral_content(prompt)

        print(generated_captions_response)
        formated_captions_response= format_caption_text_product(generated_captions_response)

            
        formated_captions_response=formated_captions_response[:-1]
        captions_response={
            "captions":formated_captions_response
        }
        response={
            "status": ResponseValues.SUCCESS,
            "message": "captions generated successfully",
            "body": captions_response
            }
        return response
    
    except Exception as e:        
        return CustomErrorResponse.generate_response("Error", str(e), 500)


    
    
    
@router.post("/filter-generation")
async def generate_filter(data_item: Optional[FilterGenerationRequest]=None):
    try:
        if not data_item:
           return CustomErrorResponse.generate_response("Error", "Give a valid caption List", 404)
        elif not data_item.data:
           return CustomErrorResponse.generate_response("Error", "captions is Empty", 404)
        elif not data_item.type:
           return CustomErrorResponse.generate_response("Error", "type is Empty", 404)
            
            
        dataString= ', '.join(data_item.data)
        prompt= "these are my "+ data_item.type+":" +dataString+" based on these give me 5 one word categories for filter in this format: ['category1','category2','category3','category4','category5']"
        filter_values_string = generate_mixtral_content(prompt)
        
        filter_values=[]
        filter_values=extract_filter_values_array(filter_values_string)
        if filter_values==[]:
           return CustomErrorResponse.generate_response("Error", "Error Generating filters", 404)

       
        response = {
                "status": ResponseValues.SUCCESS,
                "message": "captions generated successfully",
                "body": filter_values
            }
        return response
    except Exception as e:
        return CustomErrorResponse.generate_response("Error", str(e), 500)



@router.post("/tone-change")
async def generate_product_desc(req: ToneGenerationRequest):
    try:
        if not req.data:
           return CustomErrorResponse.generate_response("Error", "Data is Empty", 404)
        elif not req.social:
           return CustomErrorResponse.generate_response("Error", "Social handle is Empty", 404)
       
        prompt=""       
        if req.social=="LinkedIn":
            prompt="change the tone of this senetence more professionally for LinkedIn :"+ req.data
        elif req.social=="Facebook":
            prompt="change the tone of this senetence more likely for facebook :"+ req.data
        elif req.social=="Instagram":
            prompt="change the tone of this senetence more likely for Instagram :"+ req.data
        else:
            return CustomErrorResponse.generate_response("Error", "Please ender a valid platform", 404)
       
        generated_response = generate_mixtral_content(prompt)
       
        response = {
                "status": ResponseValues.SUCCESS,
                "message": "captions generated successfully",
                "body": remove_s_tag(generated_response)
            }
        return response
    except Exception as e:
        return CustomErrorResponse.generate_response("Error", str(e), 500)
