"""Support for PETLIBRO binary sensors."""

from __future__ import annotations

from dataclasses import dataclass
from logging import getLogger
from collections.abc import Callable
from functools import cached_property

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription, BinarySensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .devices import Device
from .devices.feeders.granary_smart_feeder import GranarySmartFeeder
from .entity import PetLibroEntity, _DeviceT, PetLibroEntityDescription
from . import PetLibroHubConfigEntry

_LOGGER = getLogger(__name__)


@dataclass(frozen=True)
class PetLibroBinarySensorEntityDescription(BinarySensorEntityDescription, PetLibroEntityDescription[_DeviceT]):
    """A class that describes device binary sensor entities."""

    should_report: Callable[[_DeviceT], bool] = lambda _: True


class PetLibroBinarySensorEntity(PetLibroEntity[_DeviceT], BinarySensorEntity):  # type: ignore [reportIncompatibleVariableOverride]
    """PETLIBRO binary sensor entity."""

    entity_description: PetLibroBinarySensorEntityDescription[_DeviceT]  # type: ignore [reportIncompatibleVariableOverride]

    @cached_property
    def is_on(self) -> bool:
        """Return True if the binary sensor is on."""
        return bool(getattr(self.device, self.entity_description.key))

DEVICE_BINARY_SENSOR_MAP: dict[type[Device], list[PetLibroBinarySensorEntityDescription]] = {
    GranarySmartFeeder: [
        PetLibroBinarySensorEntityDescription[GranarySmartFeeder](
            key="food_low",
            translation_key="food_low",
            icon="mdi:bowl-mix-outline",
            device_class=BinarySensorDeviceClass.PROBLEM
        )
    ]
}

async def async_setup_entry(
    _: HomeAssistant,
    entry: PetLibroHubConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PETLIBRO binary sensors using config entry."""
    hub = entry.runtime_data
    entities = [
        PetLibroBinarySensorEntity(device, hub, description)
        for device in hub.devices
        for device_type, entity_descriptions in DEVICE_BINARY_SENSOR_MAP.items()
        if isinstance(device, device_type)
        for description in entity_descriptions
    ]
    async_add_entities(entities)
