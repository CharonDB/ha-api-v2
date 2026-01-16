from homeassistant.helpers.area_registry import AreaRegistry, AreaEntry
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from models.dynamic_model import create_pydantic_from_ha

app = FastAPI()

class AreasView:
    url = "/areas"
    name = "v2:api:fastapi:areas"
    requires_auth = True

    @app.get("/areas")
    async def list_areas(request: Request):
        hass = request.scope["hass"]
        registry = AreaRegistry(hass)
        ha_areas = registry.async_list_areas()

        if not ha_areas:
            return []

        # Create a Pydantic model from the first HA object
        PydanticArea = create_pydantic_from_ha("AreaEntry", ha_areas[0])
        return jsonable_encoder([PydanticArea(**area.__dict__) for area in ha_areas])
