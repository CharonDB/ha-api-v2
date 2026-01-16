from homeassistant.components.http import async_register_http_view
from .registry_view import RegistryView
from .registry_config import REGISTRIES
from const import API_BASE
from fastapi.encoders import jsonable_encoder
from models.dynamic_model import create_pydantic_from_ha

class OpenAPIView(RegistryView):
    url = f"{API_BASE}/openapi.json"
    name = "v2:api:openapi"

    def __init__(self, registries):
        self.registries = registries
        self.requires_auth = True

    async def get(self, request):
        hass = request.app["hass"]
        openapi = {
            "openapi": "3.0.3",
            "info": {"title": "HomeAssistant V2 API (OpenAPI)", "version": "1.0.0"},
            "paths": {},
            "components": {"schemas": {}},
        }

        for reg in self.registries:
            objects = reg["ha_get"](hass)
            if not objects:
                continue

            model_name = f"Pydantic{reg['name'].title()}"
            Model = create_pydantic_from_ha(model_name, objects[0])
            schema = Model.schema()

            openapi["paths"][f"{API_BASE}/{reg['name']}"] = {
                "get": {
                    "summary": f"List {reg['name']}",
                    "responses": {
                        "200": {
                            "description": reg['name'].capitalize(),
                            "content": {"application/json": {"schema": {"type": "array", "items": schema}}},
                        }
                    },
                }
            }
            openapi["components"]["schemas"][model_name] = schema

        return jsonable_encoder(openapi)


def register_routes(hass):
    # Register registry endpoints dynamically
    for reg in REGISTRIES:
        async_register_http_view(hass, RegistryView(reg["name"], reg["ha_get"]))

    # Register OpenAPI endpoint
    async_register_http_view(hass, OpenAPIView(REGISTRIES))
