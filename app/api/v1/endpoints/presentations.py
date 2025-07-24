"""
API endpoints for managing presentations having entry point for all HTTP requests related to creating, checking, and downloading and customising presentations.
"""
from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import FileResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi_cache.decorator import cache

from app.api.v1.schemas.presentation_schemas import *
from app.services.presentation_service import presentation_service
from app.services.storage_service import storage_service
from app.core.custom_exceptions import PresentationNotFoundException
from app.core.config import settings, logger
from app.api.v1.dependencies import get_api_key

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post(
    "/",
    response_model=PresentationCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Queue a New Presentation",
    description="Accepts a topic and configuration, then enqueues a background job to generate the presentation. Returns immediately with a job ID and status URL.",
)
@limiter.limit(settings.CREATE_RATE_LIMIT)
async def create_presentation(
    request: Request,
    create_request: PresentationCreateRequest,
    api_key: str = Depends(get_api_key)
):
    """
        Accepts a presentation request and enqueues it for processing using ARQ.
    """
    logger.info(f"Queueing presentation on topic: {create_request.topic}")
    
    # We call our presentation_service to create an initial record for this presentation in our storage (Redis), with a status of "pending".
    presentation = presentation_service.create_new_presentation(create_request)
    
    # Enqueue the job using the ARQ pool from the app state.
    # We get the arq_pool (our connection to the Redis task queue) and use it to enqueue a job.
    arq_pool: ArqRedis = request.app.state.arq_pool
    await arq_pool.enqueue_job("generate_presentation_task", presentation.id)
    
    # Our API respond immediately without waiting for the slow generation process to finish as the task is queued now.

    # We create a URL that the client can use to check the status of the presentation.
    status_url = request.url_for("get_presentation_details", id=presentation.id)
    return PresentationCreateResponse(
        message="Presentation generation queued successfully.",
        presentation_id=presentation.id,
        status_url=str(status_url),
    )

@router.get("/{id}", response_model=PresentationStatusResponse)
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
@cache(expire=60)
# It'll automatically caches the response in Redis for 60 seconds. 
# If another request for the same ID arrives within that minute, FastAPI returns the cached result instantly without running the code again.
def get_presentation_details(request: Request, id: str, api_key: str = Depends(get_api_key)):
    try:
        return storage_service.get_presentation(id)
    except PresentationNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{id}/download", response_class=FileResponse)
# Defined response_class to tells FastAPI that the response is not JSON but a pptx file. FastAPI will handle streaming the file content to the client.
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
def download_presentation(request: Request, id: str, api_key: str = Depends(get_api_key)):
    try:
        presentation = storage_service.get_presentation(id)
        if presentation.status != "completed" or not presentation.file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Presentation not available. Status: {presentation.status}"
            )
        filename = f"{presentation.topic.replace(' ', '_').lower()}.pptx"
        return FileResponse(
            path=presentation.file_path,
            media_type='application/vnd.openxmlformats-officedocument.presentationml.presentation',
            filename=filename
        )
    except PresentationNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/{id}/configure", response_model=PresentationStatusResponse)
@limiter.limit(settings.DEFAULT_RATE_LIMIT)
def configure_presentation(
    request: Request,
    id: str,
    config_request: PresentationConfigureRequest,
    api_key: str = Depends(get_api_key),
):
    try:
        presentation = storage_service.get_presentation(id)

        if presentation.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot configure presentation. Status is '{presentation.status}'.",
            )

        # Get only the fields the user actually sent in the request
        update_data = config_request.model_dump(exclude_unset=True)
        if update_data:
            # Safely create an updated config object
            updated_config = presentation.config.model_copy(update=update_data)
            presentation.config = updated_config
            storage_service.save_presentation(presentation)
            logger.info(f"Re-configured presentation {id} with: {update_data}")

        return presentation
    except PresentationNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))