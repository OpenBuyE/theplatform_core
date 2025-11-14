import datetime

def log(message: str):
    """
    Simple logging system for debugging and auditing.
    """
    timestamp = datetime.datetime.utcnow().isoformat()
    print(f"[{timestamp}] {message}")
