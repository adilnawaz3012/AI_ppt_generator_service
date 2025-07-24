from pydantic import BaseModel
from typing import Optional, List, Literal
from app.models.presentation_models import Presentation, CustomColors

# Request body for creating a presentation
class PresentationCreateRequest(BaseModel):
    topic: str
    num_slides: int = 5
    template_name: str = "default_light"
    aspect_ratio: Literal["16:9", "4:3"] = "16:9"
    custom_content: Optional[List[dict]] = None
    custom_colors: Optional[CustomColors] = None
    custom_font: Optional[str] = None

# Response model for successful creation
class PresentationCreateResponse(BaseModel):
    message: str
    presentation_id: str
    status_url: str

# Response model for retrieving presentation details
class PresentationStatusResponse(Presentation):
    pass

# Request body for configuring an existing presentation
class PresentationConfigureRequest(BaseModel):
    num_slides: Optional[int] = None
    template_name: Optional[str] = None
    aspect_ratio: Optional[Literal["16:9", "4:3"]] = None