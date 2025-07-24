class PresentationNotFoundException(Exception):
    """Raised when a presentation ID is not found."""
    pass

class ContentGenerationException(Exception):
    """Raised when content generation fails."""
    pass