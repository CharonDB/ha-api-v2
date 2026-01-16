from homeassistant.components.http import HomeAssistantView
from fastapi.encoders import jsonable_encoder
from models.dynamic_model import create_pydantic_from_ha
from const import API_BASE

class RegistryView(HomeAssistantView):
    requires_auth = True

    def __init__(self, name: str, ha_getter):
        self.name = name
        self.ha_getter = ha_getter
        self.url = f"{API_BASE}/{name}"
        self.name_attr = f"v2:api:{name}"

    async def get(self, request):
        hass = request.app["hass"]
        objects = self.ha_getter(hass)
        if not objects:
            return []

        Model = create_pydantic_from_ha(f"Pydantic{self.name.title()}", objects[0])
        return jsonable_encoder([Model(**o.__dict__) for o in objects])
