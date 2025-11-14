import re

def is_valid_uuid(value: str) -> bool:
    """
    Simple UUID validator.
    """
    uuid_regex = re.compile(
        r"^[a-fA-F0-9]{8}-"
        r"[a-fA-F0-9]{4}-"
        r"[a-fA-F0-9]{4}-"
        r"[a-fA-F0-9]{4}-"
        r"[a-fA-F0-9]{12}$"
    )
    return bool(uuid_regex.match(value))

def ensure_positive_number(value: float, field_name: str):
    if value <= 0:
        raise ValueError(f"{field_name} must be positive.")
