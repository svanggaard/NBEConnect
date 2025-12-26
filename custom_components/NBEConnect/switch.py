from homeassistant.components.switch import (
    SwitchEntity,
    SwitchDeviceClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from logging import getLogger

_LOGGER = getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the NBE-RTB switches."""
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
        RTBSwitch(
            coordinator=dc,
            name="Boiler Power",
            read_key="operating_data/state", 
            write_key_on="settings/misc/start",
            write_key_off="settings/misc/stop",
            icon="mdi:power",
            dev_info=device_info
        ),
        
    ])

class RTBSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a NBE Switch."""

    def __init__(self, coordinator, name, read_key, write_key_on, write_key_off, icon, dev_info, is_pump=False):
        super().__init__(coordinator)
        self.read_key = read_key
        self.write_key_on = write_key_on
        self.write_key_off = write_key_off
        self.sensorname = name
        self._attr_icon = icon
        self._attr_device_class = SwitchDeviceClass.SWITCH
        self._dev_info = dev_info
        self._attr_unique_id = f"{coordinator.entry_id}_{read_key}_switch"
        self._is_pump = is_pump

    @property
    def name(self):
        return f"NBE {self.sensorname}"

    @property
    def is_on(self):
        val = self.coordinator.rtbdata.get(self.read_key)
        
        if val is None:
            return None

        if self.read_key == "operating_data/state":
            return str(val) != "14"
            
        return str(val) != "0"

    async def async_turn_on(self, **kwargs):
        _LOGGER.info(f"NBE Switch {self.name}: Turning ON")
        await self._send_command(self.write_key_on, "1")

    async def async_turn_off(self, **kwargs):
        _LOGGER.info(f"NBE Switch {self.name}: Turning OFF")
        val_to_send = "0" if self._is_pump else "1"
        await self._send_command(self.write_key_off, val_to_send)

    async def _send_command(self, key, value):
        proxy = self.coordinator.proxy
        if proxy:
            try:
                await self.coordinator.hass.async_add_executor_job(proxy.set, key, value)
            except (OSError, IOError) as e:
                _LOGGER.warning(f"NBEConnect: Command sent but response decode failed (expected). Error: {e}")
            
            await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        return self._dev_info
