"""Use the built-in Whirlpool connection; never create a second cloud session."""
import asyncio
import json
import logging
from importlib.metadata import version
from pathlib import Path
from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers import discovery, entity_registry
DOMAIN = "whirlpool_extras"
CONFIG_SCHEMA = __import__("voluptuous").Schema({DOMAIN: __import__("voluptuous").Schema({})}, extra=__import__("voluptuous").ALLOW_EXTRA)
_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    async def monitor():
        status = Path(hass.config.path(".whirlpool-migration-status.json"))
        try:
            if version("whirlpool-sixth-sense") != "2.0.3":
                raise RuntimeError("Expected whirlpool-sixth-sense 2.0.3")
            for _ in range(90):
                entries = hass.config_entries.async_entries("whirlpool")
                if entries and all(e.state is ConfigEntryState.LOADED for e in entries):
                    break
                await asyncio.sleep(2)
            else:
                raise RuntimeError("Whirlpool entries did not load")
            appliances = [a for e in entries for a in e.runtime_data.aircons]
            if not appliances:
                raise RuntimeError("No air conditioners")
            for a in appliances:
                if not type(a).__module__.startswith("whirlpool.httpapi."):
                    raise RuntimeError("AWS IoT/unknown backend: unsupported extra controls")
                for getter, setter in (("get_quiet_mode", "set_quiet_mode"), ("get_turbo_mode", "set_turbo_mode"), ("get_eco_mode", "set_eco_mode"), ("get_display_on", "set_display_on")):
                    if not callable(getattr(a, setter, None)) or type(getattr(a, getter)()) is not bool:
                        raise RuntimeError("Missing control or unknown state")
            registry = entity_registry.async_get(hass)
            devices = {row.unique_id: row.device_id for row in registry.entities.values() if row.platform == DOMAIN}
            hass.data[DOMAIN] = {"appliances": appliances, "entities": [], "devices": devices}
            await discovery.async_load_platform(hass, "switch", DOMAIN, {}, config)
            for _ in range(45):
                entities = hass.data[DOMAIN]["entities"]
                if len(entities) == 3 * len(appliances) and all(e.entity_id and (s := hass.states.get(e.entity_id)) and s.state in ("on", "off") for e in entities):
                    break
                await asyncio.sleep(2)
            else:
                raise RuntimeError("Not all three extra switches have valid states")
            payload = {"ok": True, "switches": [e.entity_id for e in entities]}
        except Exception as exc:
            _LOGGER.exception("Whirlpool Extras startup validation failed")
            payload = {"ok": False, "error": str(exc)}
        def write():
            temp = status.with_suffix(".tmp")
            temp.write_text(json.dumps(payload))
            temp.replace(status)
        await hass.async_add_executor_job(write)
    hass.async_create_background_task(monitor(), "Whirlpool Extras startup validation")
    return True
