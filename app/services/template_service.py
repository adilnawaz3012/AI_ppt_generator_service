import json
from pathlib import Path
from pydantic import BaseModel, ValidationError
from app.core.config import logger

# Adding below logic to make sure the server and worker both have access to same path.
# This calculates the absolute path to the templates directory inside the container.
# Path(__file__) is /app/app/services/template_service.py
# .parent.parent.parent is /app
# So, TEMPLATE_DIR is /app/templates
BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"

class TemplateColors(BaseModel):
    background: str
    text: str
    title: str
    accent: str

class Template(BaseModel):
    name: str
    description: str
    colors: TemplateColors
    font: str

class TemplateService:
    def __init__(self):
        self.template_path = TEMPLATE_DIR
        self.cache: dict[str, Template] = {}

    def load_template(self, name: str) -> Template:
        """Loads a template by name using a absolute path."""
        if name in self.cache:
            return self.cache[name]

        file_path = self.template_path / f"{name}.json"
        if not file_path.exists():
            logger.error(f"FATAL: Template '{name}' not found at absolute path: {file_path}")
            raise FileNotFoundError(f"Template '{name}' not found.")
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                template = Template(**data)
                self.cache[name] = template
                return template
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Failed to load or validate template '{name}': {e}")
            raise ValueError(f"Invalid template file: {name}.json")

template_service = TemplateService()