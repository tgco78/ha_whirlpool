"""Four extra switches sharing the built-in integration's appliances."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback
from homeassistant.helpers import entity_registry
from homeassistant.exceptions import HomeAssistantError
from . import DOMAIN
CONTROLS = (
    ("Jet", "_jet_mode", "turbo_mode", "mdi:weather-windy"),
    ("Power Save", "_power_save", "eco_mode", "mdi:leaf"),
    ("Kijelző", "_display", "display_on", "mdi:monitor"),
)
PARALLEL_UPDATES = 1

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    data = hass.data[DOMAIN]
    entities = [ExtraSwitch(a, control) for a in data["appliances"] for control in CONTROLS]
    data["entities"] = entities
    async_add_entities(entities)

class ExtraSwitch(SwitchEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, appliance, control):
        self.appliance = appliance
        name, suffix, self.control, icon = control
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = appliance.said + suffix
        # Registry migration retains the original Whirlpool device_id.

    @property
    def available(self):
        return self.source_current() and bool(self.appliance.get_online()) and self.is_on is not None

    def source_current(self):
        return any(self.appliance in getattr(getattr(entry, "runtime_data", None), "aircons", ()) for entry in self.hass.config_entries.async_entries("whirlpool"))

    @property
    def is_on(self):
        try:
            value = getattr(self.appliance, "get_" + self.control)()
            return value if type(value) is bool else None
        except (NotImplementedError, AttributeError):
            return None

    async def async_added_to_hass(self):
        device_id = self.hass.data[DOMAIN]["devices"].get(self.unique_id)
        if device_id:
            entity_registry.async_get(self.hass).async_update_entity(self.entity_id, device_id=device_id)
        self.appliance.register_attr_callback(self.changed)
        self.async_on_remove(lambda: self.appliance.unregister_attr_callback(self.changed))

    @callback
    def changed(self):
        self.async_write_ha_state()

    async def set_value(self, value):
        if not self.source_current():
            raise HomeAssistantError("Whirlpool connection was reloaded; restart Home Assistant")
        try:
            result = await getattr(self.appliance, "set_" + self.control)(value)
        except (NotImplementedError, AttributeError) as exc:
            raise HomeAssistantError("This backend does not support this control") from exc
        if not result:
            raise HomeAssistantError("Whirlpool rejected the command")
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        await self.set_value(True)

    async def async_turn_off(self, **kwargs):
        await self.set_value(False)
