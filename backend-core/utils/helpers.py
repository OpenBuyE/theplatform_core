from datetime import datetime
import uuid

def generate_uuid() -> str:
    """
    Generates a new UUID.
    """
    return str(uuid.uuid4())

def current_timestamp() -> str:
    """
    ISO formatted timestamp.
    """
    return datetime.utcnow().isoformat()
