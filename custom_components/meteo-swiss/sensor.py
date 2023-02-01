import logging
import pprint

from hamsclientfork import meteoSwissClient
from homeassistant.helpers.entity import Entity


from .const import (
    DOMAIN,
    SENSOR_TYPES,
    SENSOR_TYPE_CLASS,
    SENSOR_TYPE_ICON,
    SENSOR_TYPE_NAME,
    SENSOR_TYPE_UNIT,
    SENSOR_DATA_ID,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config, async_add_entities):
    _LOGGER.debug("Starting async setup platform")
    client = hass.data[DOMAIN]["client"]

    async_add_entities(
        [MeteoSwissSensor(typ, client) for typ in SENSOR_TYPES],
        True,
    )


class MeteoSwissSensor(Entity):
    def __init__(self, sensor_type, client: meteoSwissClient):
        self._client = client
        if client is None:
            _LOGGER.error("Error empty client")
        self._state = None
        self._type = sensor_type

    @property
    def name(self):
        """Return the name of the sensor."""
        x = SENSOR_TYPES[self._type][SENSOR_TYPE_NAME]
        return f"{self._data['name']} {x}"

    @property
    def unique_id(self):
        """Return the unique id of the sensor."""
        return self.name

    @property
    def state(self):

        dataId = SENSOR_TYPES[self._type][SENSOR_DATA_ID]
        try:
            return self._data["condition"][0][dataId]
        except Exception as exc:
            _LOGGER.warning("self._data['condition'][0][dataId]: %s:", exc)
            _LOGGER.warning("self._data: %s: %s", pprint.pformat(self._data))
            return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return SENSOR_TYPES[self._type][SENSOR_TYPE_UNIT]

    @property
    def icon(self):
        """Return the icon."""
        return SENSOR_TYPES[self._type][SENSOR_TYPE_ICON]

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return SENSOR_TYPES[self._type][SENSOR_TYPE_CLASS]

    def update(self):
        # self._client.update()
        self._data = self._client.get_data()
