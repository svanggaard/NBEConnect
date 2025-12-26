from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity, 
    SensorStateClass,
)
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from .protocol import Proxy
from .const import DOMAIN
from .rtbdata import RTBData
from logging import getLogger

_LOGGER = getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the NBE-RTB sensors."""
    _LOGGER.info("Setting up NBE sensors with Renamed Temperatures...")
    
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
        "model": "V7/V13 Controller",
        "configuration_url": f"http://{entry.data.get('ip_address')}" if entry.data.get('ip_address') else None
    }

    sensors = [
        RTBBinarySensor(dc, 'Boiler Running', 'operating_data/power_pct', 'boiler_power_pct', BinarySensorDeviceClass.RUNNING, icon="mdi:fire", dev_info=device_info),
        RTBBinarySensor(dc, 'Boiler Alarm', 'operating_data/off_on_alarm', 'boiler_state_off_on_alarm', BinarySensorDeviceClass.PROBLEM, icon="mdi:alert-circle", dev_info=device_info),
        RTBBinarySensor(dc, 'Boiler Pump', 'operating_data/boiler_pump_state', 'house_pump_state', None, icon="mdi:pump", dev_info=device_info),
        RTBSensor(dc, 'Temperature Boiler', 'operating_data/boiler_temp', 'boiler_temp', "°C", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, icon="mdi:thermometer", dev_info=device_info),
        RTBSensor(dc, 'Temperature Target', 'operating_data/boiler_ref', 'boiler_ref', "°C", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, icon="mdi:thermometer-check", dev_info=device_info),
        RTBSensor(dc, 'Temperature Smoke', 'operating_data/smoke_temp', 'smoke_temp', "°C", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, icon="mdi:thermometer-alert", dev_info=device_info),
        RTBSensor(dc, 'Temperature Return', 'operating_data/return_temp', 'return_temp', "°C", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, icon="mdi:thermometer-water", dev_info=device_info),
        RTBSensor(dc, 'Temperature Shaft', 'operating_data/shaft_temp', 'shaft_temp', "°C", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, icon="mdi:thermometer-lines", dev_info=device_info),
        RTBSensor(dc, 'Temperature External', 'operating_data/external_temp', 'external_temp', "°C", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, icon="mdi:thermometer", dev_info=device_info),
        RTBSensor(dc, 'Temperature DHW', 'operating_data/dhw_temp', 'dhw_temp', "°C", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, icon="mdi:water-thermometer", dev_info=device_info),
        RTBSensor(dc, 'Boiler Power %', 'operating_data/power_pct', 'power_pct', "%", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT, icon="mdi:lightning-bolt-outline", dev_info=device_info),
        RTBSensor(dc, 'Boiler Power kW', 'operating_data/power_kw', 'power_kw', "kW", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, icon="mdi:lightning-bolt", dev_info=device_info),
        RTBSensor(dc, 'Photo Sensor', 'operating_data/photo_level', 'photo_level', "lx", SensorDeviceClass.ILLUMINANCE, SensorStateClass.MEASUREMENT, icon="mdi:eye", dev_info=device_info),
        RTBSensor(dc, 'Oxygen (O2)', 'operating_data/oxygen', 'oxygen_level', "%", None, SensorStateClass.MEASUREMENT, icon="mdi:gas-cylinder", dev_info=device_info),
        RTBSensor(dc, 'Total Pellet Consumption', 'consumption_data/counter', 'pelletcounter', "kg", SensorDeviceClass.WEIGHT, SensorStateClass.TOTAL_INCREASING, icon="mdi:chart-line", dev_info=device_info), 
        RTBSensor(dc, 'Hopper Content', 'operating_data/content', 'hopper_content', "kg", SensorDeviceClass.WEIGHT, SensorStateClass.MEASUREMENT, multiplier=10, icon="mdi:silo", dev_info=device_info),
        RTBSensor(dc, 'State Code', 'operating_data/state', 'boiler_state_code', None, None, SensorStateClass.MEASUREMENT, icon="mdi:information-outline", dev_info=device_info),
    ]

    async_add_entities(sensors)
    _LOGGER.info(f"NBE Sensors updated successfully!")


class RTBSensor(CoordinatorEntity, SensorEntity):
    """Representation of an RTB sensor."""

    def __init__(self, coordinator, name, client_key, uid, unitofmeassurement, device_class, state_class, multiplier=None, icon=None, dev_info=None):
        super().__init__(coordinator)
        self.client_key = client_key
        self._device_class = device_class
        self.sensorname = name
        self.uid = uid
        self._unit_of_measurement = unitofmeassurement
        self._state_class = state_class
        self.multiplier = multiplier
        self._attr_icon = icon
        self._dev_info = dev_info

    @property
    def name(self):
        return f"NBE {self.sensorname}"

    @property
    def native_unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def unique_id(self):
        return self.uid
    
    @property
    def native_value(self):
        state = self.coordinator.rtbdata.get(self.client_key)
        
        if not state or "999.9" in str(state):
             return None
        
        if self.multiplier:
            try:
                val_float = float(state)
                return val_float * self.multiplier
            except ValueError:
                return state
                
        return state

    @property
    def device_class(self):
        return self._device_class
    
    @property
    def state_class(self):
        return self._state_class

    @property
    def device_info(self):
        return self._dev_info

class RTBBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of an RTB binary sensor."""

    def __init__(self, coordinator, name, client_key, uid, device_class, icon=None, dev_info=None):
        super().__init__(coordinator)
        self.client_key = client_key
        self._device_class = device_class
        self.sensorname = name
        self.uid = uid
        self._attr_icon = icon
        self._dev_info = dev_info

    @property
    def name(self):
        return f"NBE {self.sensorname}"

    @property
    def is_on(self):
        s = self.coordinator.rtbdata.get(self.client_key)
        if not s: return None
        return s != "0"
    
    @property
    def unique_id(self):
        return self.uid

    @property
    def device_class(self):
        return self._device_class

    @property
    def device_info(self):
        return self._dev_info
