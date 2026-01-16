from homeassistant.helpers.area_registry import AreaRegistry

REGISTRIES = [
    {
        "name": "areas",
        "ha_get": lambda hass: AreaRegistry(hass).async_list_floors(),
    },
]
