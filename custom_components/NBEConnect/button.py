from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from logging import getLogger

_LOGGER = getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    dc = hass.data[DOMAIN][entry.entry_id+'_coordinator']
    
    serial = "Unknown"
    if hasattr(dc.proxy, 'serial') and dc.proxy.serial:
        serial = dc.proxy.serial
    elif entry.data.get("serial"):
        serial = entry.data.get("serial")

    device_info = {
        "identifiers": {(DOMAIN, serial)},
        "name": "NBE Boiler",
        "manufacturer": "NBE",
        "model": "V7/V13 Controller"
    }

    async_add_entities([
        RTBSignalButton(
            coordinator=dc, 
            name="Reset Boiler Alarm", 
            path="settings/misc/reset_alarm", 
            uid="nbereset", 
            value="1",
            icon="mdi:alert-remove-outline",
            dev_info=device_info
        )
    ])

class RTBSignalButton(CoordinatorEntity, ButtonEntity):
    """Representation of a signal button."""

    def __init__(self, coordinator, name, path, uid, value, icon, dev_info):
        super().__init__(coordinator)
        self._name = name
        self._path = path
        self._value = value
        self.uid = uid
        self._attr_icon = icon
        self._dev_info = dev_info
        self._attr_unique_id = f"{coordinator.entry_id}_{uid}"

    @property
    def name(self):
        return f"NBE {self._name}"

    def press(self) -> None:
        """Press the button."""
        _LOGGER.debug(f"Async press {self._name}")
        proxy = self.coordinator.proxy
        if proxy:
            try:
                proxy.set(self._path, self._value)
            except Exception as e:
                _LOGGER.warning(f"Button press error (might be okay): {e}")
        _LOGGER.debug(f"Async press {self._name} - Done!")

    @property
    def device_info(self):
        return self._dev_info
