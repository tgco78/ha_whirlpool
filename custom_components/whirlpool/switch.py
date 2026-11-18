"""Switch platform for Whirlpool air conditioners."""

from typing import override

from whirlpool.aircon import Aircon

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import WhirlpoolConfigEntry
from .entity import WhirlpoolEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: WhirlpoolConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Whirlpool switches."""
    appliances_manager = config_entry.runtime_data

    async_add_entities(
        AirConQuietModeSwitch(aircon)
        for aircon in appliances_manager.aircons
    )


class AirConQuietModeSwitch(WhirlpoolEntity, SwitchEntity):
    """Whirlpool air conditioner Super Silent switch."""

    _appliance: Aircon

    _attr_name = "Super Silent"
    _attr_icon = "mdi:volume-mute"

    def __init__(self, appliance: Aircon) -> None:
        """Initialize the Super Silent switch."""
        super().__init__(appliance, unique_id_suffix="_quiet_mode")

    @property
    @override
    def is_on(self) -> bool | None:
        """Return whether Super Silent mode is enabled."""
        return self._appliance.get_quiet_mode()

    @override
    async def async_turn_on(self, **kwargs) -> None:
        """Enable Super Silent mode."""
        self._check_service_request(
            await self._appliance.set_quiet_mode(True)
        )

    @override
    async def async_turn_off(self, **kwargs) -> None:
        """Disable Super Silent mode."""
        self._check_service_request(
            await self._appliance.set_quiet_mode(False)
        )
