from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict
import uuid
from enum import Enum

class SlideLayout(str, Enum):
    """
        Using an Enum to ensures that we can only use predefined layouts like "title_slide" or "bullet_points", 
        preventing typos and making our code more reliable.
    """
    TITLE = "title_slide"
    BULLET_POINTS = "bullet_points"
    TWO_COLUMN = "two_column"
    CONTENT_WITH_IMAGE = "content_with_image"

class Slide(BaseModel):
    type: SlideLayout
    title: Optional[str] = None
    subtitle: Optional[str] = None
    points: Optional[List[str]] = None
    left_content: Optional[str] = None
    right_content: Optional[str] = None
    content: Optional[str] = None
    image_suggestion: Optional[str] = None

class PresentationData(BaseModel):
    title: str
    slides: List[Slide]
    citations: List[str] = []

class CustomColors(BaseModel):
    background: str
    text: str
    title: str
    accent: str

class PresentationConfig(BaseModel):
    num_slides: int = Field(5, ge=1, le=20)
    template_name: str = "default_light"
    aspect_ratio: Literal["16:9", "4:3"] = "16:9"
    custom_colors: Optional[CustomColors] = None
    custom_font: Optional[str] = None

class Presentation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str
    status: Literal["pending", "completed", "failed"] = "pending"
    config: PresentationConfig
    content: Optional[PresentationData] = None
    file_path: Optional[str] = None
    error_message: Optional[str] = None
