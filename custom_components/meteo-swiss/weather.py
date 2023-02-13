import datetime
import logging

from typing import Any

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_TIME,
    WeatherEntity,
)
from homeassistant.const import (
    TEMP_CELSIUS,
    SPEED_KILOMETERS_PER_HOUR,
    PRESSURE_HPA,
)


from .const import (
    CONF_FORECAST_NAME,
    CONF_POSTCODE,
    CONF_STATION,
    CONDITION_CLASSES,
    DOMAIN,
)


from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from . import MeteoSwissDataUpdateCoordinator


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up weather entity."""
    _LOGGER.debug("Starting async setup platform for weather")
    c: MeteoSwissDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MeteoSwissWeather(entry.entry_id, c)], True)


class MeteoSwissWeather(
    CoordinatorEntity[MeteoSwissDataUpdateCoordinator],
    WeatherEntity,
):
    _attr_native_temperature_unit = TEMP_CELSIUS
    _attr_native_pressure_unit = PRESSURE_HPA
    _attr_native_wind_speed_unit = SPEED_KILOMETERS_PER_HOUR

    def __init__(
        self,
        integration_id: str,
        coordinator: MeteoSwissDataUpdateCoordinator,
    ):
        super().__init__(coordinator)
        self._attr_unique_id = "weather.%s" % integration_id
        self._attr_station = coordinator.data[CONF_STATION]
        self._attr_post_code = coordinator.data[CONF_POSTCODE]
        self.__set_data(coordinator.data)

    def __set_data(self, data: dict[str, Any]):
        self._displayName = data[CONF_FORECAST_NAME]
        self._forecastData = data["forecast"]
        self._condition = data["condition"]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle data update."""
        data = self.coordinator.data
        self.__set_data(data)
        self.async_write_ha_state()

    @property
    def name(self):
        return self._displayName

    @property
    def native_temperature(self):
        if not self._condition:
            # Real-time weather station provides no data.
            return
        try:
            return float(self._condition[0]["tre200s0"])
        except Exception:
            _LOGGER.exception("Error converting temp: %s", self._condition)

    @property
    def native_pressure(self):
        if not self._condition:
            # Real-time weather station provides no data.
            return
        try:
            return float(self._condition[0]["prestas0"])
        except Exception:
            _LOGGER.exception(
                "Error converting pressure (qfe): %s",
                self._condition,
            )

    @property
    def pressure_qff(self):
        if not self._condition:
            # Real-time weather station provides no data.
            return
        try:
            return float(self.condition[0]["pp0qffs0"])
        except Exception:
            _LOGGER.exception(
                "Error converting pressure (qff): %s",
                self._condition,
            )

    @property
    def pressure_qnh(self):
        if not self._condition:
            # Real-time weather station provides no data.
            return
        try:
            return float(self.condition[0]["pp0qnhs0"])
        except Exception:
            _LOGGER.exception(
                "Error converting pressure (qnh): %s",
                self._condition,
            )

    @property
    def state(self):
        symbolId = self._forecastData["currentWeather"]["icon"]
        cond = next(
            (k for k, v in CONDITION_CLASSES.items() if int(symbolId) in v),
            None,
        )
        _LOGGER.debug(
            "Current symbol is %s condition is: %s",
            symbolId,
            cond,
        )
        return cond

    def msSymboldId(self):
        return self._forecastData["currentWeather"]["icon"]

    @property
    def humidity(self):
        if not self._condition:
            # Real-time weather station provides no data.
            return
        try:
            return float(self._condition[0]["ure200s0"])
        except Exception:
            _LOGGER.exception(
                "Unable to convert humidity value: %s",
                self._condition,
            )

    @property
    def native_wind_speed(self):
        if not self._condition:
            # Real-time weather station provides no data.
            return
        try:
            return float(self._condition[0]["fu3010z0"])
        except Exception:
            _LOGGER.exception(
                "Unable to convert windSpeed value: %s",
                self._condition,
            )

    @property
    def attribution(self):
        a = "Data provided by MeteoSwiss."
        a += "  Forecasts from postal code %s." % (self._attr_post_code,)
        if self._attr_station:
            a += "  Real-time weather data from weather station %s" % (
                self._attr_station,
            )
        return a

    @property
    def wind_bearing(self):
        if not self._condition:
            # Real-time weather station provides no data.
            return
        try:
            return self._condition[0]["dkl010z0"]
        except Exception:
            _LOGGER.exception(
                "Unable to get wind_bearing from data: %s",
                self._condition,
            )

    @property
    def forecast(self):
        currentDate = datetime.datetime.now()
        one_day = datetime.timedelta(days=1)
        fcdata_out = []
        # Skip the first element - it's the forecast for the current day
        for forecast in self._forecastData["regionForecast"][1:]:
            # calculating date of the forecast
            currentDate = currentDate + one_day
            data_out = {}
            data_out[ATTR_FORECAST_TIME] = currentDate.strftime("%Y-%m-%d")
            data_out[ATTR_FORECAST_NATIVE_TEMP_LOW] = float(
                forecast["temperatureMin"],
            )
            data_out[ATTR_FORECAST_NATIVE_TEMP] = float(
                forecast["temperatureMax"],
            )
            data_out[ATTR_FORECAST_CONDITION] = next(
                (
                    k
                    for k, v in CONDITION_CLASSES.items()
                    if int(forecast["iconDay"]) in v
                ),
                None,
            )
            fcdata_out.append(data_out)
        return fcdata_out
