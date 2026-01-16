from pydantic import BaseModel, create_model
from typing import Any, List, Dict, Optional

def create_pydantic_from_ha(name: str, ha_obj: Any, exclude_private: bool = True) -> BaseModel:
    """
    Dynamically creates a Pydantic model from any HA registry entry object.

    Args:
        name: Name of the Pydantic model
        ha_obj: HA registry object instance (AreaEntry, DeviceEntry, etc.)
        exclude_private: Whether to ignore fields starting with `_`

    Returns:
        A Pydantic model class
    """
    fields: Dict[str, tuple] = {}
    for attr_name, value in ha_obj.__dict__.items():
        if exclude_private and attr_name.startswith("_"):
            continue

        # Convert sets to list for JSON serialization
        if isinstance(value, set):
            fields[attr_name] = (List[Any], list(value))
        # Optional for None
        elif value is None:
            fields[attr_name] = (Optional[type(value)], None)
        else:
            fields[attr_name] = (type(value), value)

    return create_model(name, **fields)
