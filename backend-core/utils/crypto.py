import hashlib

def sha256(data: str) -> str:
    """
    Returns SHA-256 hash of the input string.
    """
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def hash_purchase_data(purchase_id: str, amount: float, timestamp: str) -> str:
    """
    Hashes key purchase fields for deterministic adjudication seeds.
    """
    raw = f"{purchase_id}-{amount}-{timestamp}"
    return sha256(raw)
