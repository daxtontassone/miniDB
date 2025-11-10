# Serialization helpers for encoding/decoding rows.
# Handles varints, null bitmaps, and type-specific serialization.

# Placeholder for serialization helpers (to be expanded later).
# For now: simple utilities like boolean coercion.

def to_bool(val) -> bool:
    """Convert arbitrary input to a boolean, using common truthy strings."""
    if isinstance(val, bool): 
        return val
    if isinstance(val, str):
        return val.lower() in ("1", "true", "t", "yes", "y")
    return bool(val)
