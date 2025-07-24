import json
import redis
from typing import Optional
from app.models.presentation_models import Presentation
from app.core.custom_exceptions import PresentationNotFoundException
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL)
STORAGE_KEY_PREFIX = "presentation:"

class StorageService:
    """
        StorageService class acts as the dedicated data access layer for application. 
        It handles all the logic for saving and retrieving presentation data from your Redis instance.
    """
    def save_presentation(self, presentation: Presentation):
        """Saves a presentation object to Redis by serializing it to JSON."""
        key = f"{STORAGE_KEY_PREFIX}{presentation.id}"
        # Convert the Pydantic model to a JSON string for storage, Since Redis can only store simple strings, it serializes the complex Python object into a JSON string.
        value = presentation.model_dump_json() 
        redis_client.set(key, value)

    def get_presentation(self, presentation_id: str) -> Optional[Presentation]:
        """Retrieves and deserializes a presentation object from Redis."""
        key = f"{STORAGE_KEY_PREFIX}{presentation_id}"
        
        stored_data = redis_client.get(key)
        
        if not stored_data:
            raise PresentationNotFoundException(f"Presentation with ID '{presentation_id}' not found.")
        
        # Convert the JSON string from Redis back into a Pydantic model
        return Presentation.model_validate_json(stored_data)

storage_service = StorageService()