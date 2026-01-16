from homeassistant.core import HomeAssistant
from openapi import register_routes

async def async_setup(hass: HomeAssistant, config: dict):
    register_routes(hass)
    return True
