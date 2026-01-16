from homeassistant.helpers.floor_registry import FloorRegistry, FloorEntry
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from models.dynamic_model import create_pydantic_from_ha

app = FastAPI()

class AreasView:
    url = "/floors"
    name = "v2:api:fastapi:floors"
    requires_auth = True

    @app.get("/floors")
    async def list_floors(request: Request):
        hass = request.scope["hass"]
        registry = FloorRegistry(hass)
        ha_floors = registry.async_list_floors()

        if not ha_floors:
            return []

        # Create a Pydantic model from the first HA object
        PydanticFloor = create_pydantic_from_ha("FloorEntry", ha_floors[0])
        return jsonable_encoder([PydanticFloor(**floor.__dict__) for floor in ha_floors])
