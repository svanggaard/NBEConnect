from homeassistant.components.number import (
    NumberEntity,
    NumberDeviceClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from logging import getLogger

_LOGGER = getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the NBE-RTB numbers."""
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
        RTBNumber(
            coordinator=dc, 
            name='Boiler Target Temp', 
            read_key='operating_data/boiler_ref', 
            write_key='settings/boiler/temp', 
            unit="°C", 
            min_val=10, 
            max_val=85,
            read_multiplier=1,
            write_multiplier=1, 
            icon="mdi:thermometer-check",
            dev_info=device_info
        ),
        
        RTBNumber(
            coordinator=dc, 
            name='Hopper Content', 
            read_key='operating_data/content', 
            write_key='settings/hopper/content', 
            unit="kg", 
            min_val=0, 
            max_val=9000, 
            read_multiplier=10,
            write_multiplier=1,
            icon="mdi:silo",
            dev_info=device_info
        ),
    ])

class RTBNumber(CoordinatorEntity, NumberEntity):

    def __init__(self, coordinator, name, read_key, write_key, unit, min_val, max_val, read_multiplier=1, write_multiplier=1, icon=None, dev_info=None):
        super().__init__(coordinator)
        self.read_key = read_key
        self.write_key = write_key
        self.sensorname = name
        self._attr_native_unit_of_measurement = unit
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_device_class = NumberDeviceClass.TEMPERATURE if "Temp" in name else NumberDeviceClass.WEIGHT
        self._attr_unique_id = f"{coordinator.entry_id}_{write_key}"
        
        self.read_multiplier = read_multiplier
        self.write_multiplier = write_multiplier
        self._attr_icon = icon
        self._dev_info = dev_info

    @property
    def name(self):
        return f"NBE {self.sensorname}"

    @property
    def native_value(self):
        val = self.coordinator.rtbdata.get(self.read_key)
        try:
            if val:
                return float(val) * self.read_multiplier
            return None
        except ValueError:
            return None

    @property
    def device_info(self):
        return self._dev_info

    async def async_set_native_value(self, value: float) -> None:
        _LOGGER.info(f"Setting NBE value for {self.write_key} to {value}")
        
        proxy = self.coordinator.proxy
        
        if proxy:
            try:
                val_to_send = int(value * self.write_multiplier)
                
                await self.coordinator.hass.async_add_executor_job(proxy.set, self.write_key, str(val_to_send))
            
            except (OSError, IOError) as e:
                _LOGGER.warning(f"NBEConnect: Command sent via {self.write_key}, but response decode failed (expected). Error: {e}")
            except Exception as e:
                _LOGGER.error(f"NBEConnect: Unexpected error: {e}")
             
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("NBEConnect: Cannot find 'proxy' in coordinator to send command!")
