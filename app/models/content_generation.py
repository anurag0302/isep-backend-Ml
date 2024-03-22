from pydantic import BaseModel, create_model, Field
from typing import List,Optional, Dict

class BaseResponse(BaseModel):
    status: str
    message: str

def create_success_response(body_model):
    return create_model(
        f"Success{body_model.__name__}Response",
        body=(body_model, ...),
        __base__=BaseResponse
    )

class CaptionResponse(BaseModel):
    captions: List[str]

class Filters(BaseModel):
    mood: Optional[str] = None
    category: Optional[List[str]] = None
    tone: Optional[str] = None
    length: Optional[str] = None
    app: Optional[List[str]] = None
    sort: Optional[str] = None

class CaptionGenerationRequest(BaseModel):
    objects: List[str]
    image_description: str   
    filters: Optional[Filters] = None
    
    
class ObjectResponse(BaseModel):
    objects: List[str]
    image_description: str
    
class hashtagsGenerationRequest(BaseModel):
    objects: List[str] = None
    image_description: str = None
    filters: Optional[Filters] = None
    
    
class HashtagsResponse(BaseModel):
    hashtags: List[str]
    
class GenerateDescriptionCaption(BaseModel):
    description: str = None
    filters: Optional[Filters] = None
    
    
class FilterGenerationRequest(BaseModel):
    data: Optional[list[str]] = None
    type: Optional[str] = None  
    

class ToneGenerationRequest(BaseModel):
    data: str = Field(None)
    social: str = Field(None)
    
    
    
SuccessCaptionsResponse = create_success_response(CaptionResponse)
SuccessObjectsResponse = create_success_response(ObjectResponse)
SuccessHashtagsResponse = create_success_response(HashtagsResponse)
