from arq.connections import RedisSettings
from app.core.config import settings, logger
from app.services.storage_service import storage_service
from app.services.content_service import content_service
from app.services.template_service import template_service, Template, TemplateColors
from app.utils.pptx_builder import create_presentation_file

async def generate_presentation_task(ctx, presentation_id: str):
    presentation = storage_service.get_presentation(presentation_id)
    if not presentation:
        logger.error(f"Task started for non-existent presentation ID: {presentation_id}")
        return
    try:
        logger.info(f"[ARQ Task {presentation.id}] Starting generation.")

        template: Template
        
        # Check if custom values were provided and update the temaplate accordingly
        if presentation.config.custom_colors and presentation.config.custom_font:
            logger.info("Using custom colors and font for generation.")
            template = Template(
                name="custom",
                description="Custom user-defined template",
                colors=TemplateColors(**presentation.config.custom_colors.model_dump()),
                font=presentation.config.custom_font
            )
        else:
            logger.info(f"Loading template from file: {presentation.config.template_name}")
            template = template_service.load_template(presentation.config.template_name)

        presentation.content = await content_service.generate_content_from_topic(
            topic=presentation.topic,
            num_slides=presentation.config.num_slides,
        )
        
        presentation.file_path = create_presentation_file(
            data=presentation.content,
            config=presentation.config,
            template=template,
        )
        
        presentation.status = "completed"
        logger.info(f"[ARQ Task {presentation.id}] Generation successful.")

    except Exception as e:
        presentation.status = "failed"
        presentation.error_message = str(e)
        logger.error(f"[ARQ Task {presentation.id}] Generation failed: {e}", exc_info=True)
 
    finally:
        storage_service.save_presentation(presentation)

class WorkerSettings:
    """
        WorkerSettings class is not run our code directly  but is used by the ARQ command-line tool to configure and start the worker.
    """
    functions = [generate_presentation_task]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    max_jobs = 5