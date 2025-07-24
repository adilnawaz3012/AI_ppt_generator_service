from app.models.presentation_models import Presentation, PresentationConfig
from app.api.v1.schemas.presentation_schemas import PresentationCreateRequest
from .storage_service import storage_service
from app.core.config import logger

class PresentationService:
    """
        PresentationService class acts as a important middle layer. 
        Its sole responsibility is to take an incoming request from the API and create the initial "pending" record for the presentation job,
        which later to be returned to the user(s) with API to check the status of the presentaion creation.
    """
    def create_new_presentation(self, request: PresentationCreateRequest) -> Presentation:
        config = PresentationConfig(
            num_slides=request.num_slides,
            template_name=request.template_name,
            aspect_ratio=request.aspect_ratio,
            custom_colors=request.custom_colors,
            custom_font=request.custom_font,
        )
        presentation = Presentation(topic=request.topic, config=config)
        storage_service.save_presentation(presentation)
        logger.info(f"Created pending presentation record with ID: {presentation.id}")
        return presentation

presentation_service = PresentationService()