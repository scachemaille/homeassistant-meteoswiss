"""Config flow to configure the Meteo-Swiss integration."""
import logging

import re
import voluptuous as vol
from homeassistant import config_entries
from .const import (
    DOMAIN,
    CONF_LAT,
    CONF_LON,
    CONF_NAME,
    CONF_POSTCODE,
    CONF_STATION,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
)
from hamsclientfork import meteoSwissClient


_LOGGER = logging.getLogger(__name__)


class MeteoSwissFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Init FlowHandler."""
        super().__init__()
        self._lat = None
        self._lon = None
        self._post_code = None
        self._stations_map = None
        self._stations = None

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""

        _LOGGER.debug(
            "step user: starting with lat %s lon %s post %s",
            self._lat,
            self._lon,
            self._post_code,
        )

        def data_schema(lat, lon):
            return vol.Schema(
                {
                    vol.Required(
                        CONF_LAT,
                        default=lat,
                    ): float,
                    vol.Required(
                        CONF_LON,
                        default=lon,
                    ): float,
                }
            )

        errors = {}
        if user_input is not None:
            if user_input[CONF_LAT] > 90 or user_input[CONF_LAT] < -90:
                errors["lat"] = "latitude_error"
            if user_input[CONF_LON] > 180 or user_input[CONF_LON] < -180:
                errors["lon"] = "longitude_error"
            schema = data_schema(user_input[CONF_LAT], user_input[CONF_LON])
        else:
            schema = data_schema(
                self.hass.config.latitude,
                self.hass.config.longitude,
            )

        if errors or user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=schema, errors=errors
            )

        self._lat = user_input[CONF_LAT]
        self._lon = user_input[CONF_LON]
        _LOGGER.debug(
            "step user: continuing with lat %s lon %s post %s",
            self._lat,
            self._lon,
            self._post_code,
        )
        return await self.async_step_user_two()

    async def async_step_user_two(self, user_input=None):
        """Handle the second step of setup."""

        _LOGGER.debug(
            "step user two: starting with lat %s lon %s post %s",
            self._lat,
            self._lon,
            self._post_code,
        )

        def data_schema(postcode):
            return vol.Schema(
                {
                    vol.Required(
                        CONF_POSTCODE,
                        default=postcode,
                    ): str,
                }
            )

        client = await self.hass.async_add_executor_job(
            meteoSwissClient,
            "No display name",
            user_input.get(CONF_POSTCODE) if user_input else None,
        )

        errors = {}
        if user_input is not None:
            if not re.match(r"^\d{4}$", str(user_input[CONF_POSTCODE])):
                errors[CONF_POSTCODE] = "invalid_postcode"

            schema = data_schema(
                user_input[CONF_POSTCODE],
            )
        else:
            postcode = await self.hass.async_add_executor_job(
                client.getPostCode, self._lat, self._lon
            )

            schema = data_schema(
                postcode,
            )

        if errors or user_input is None:
            return self.async_show_form(
                step_id="user_two", data_schema=schema, errors=errors
            )

        self._post_code = int(user_input[CONF_POSTCODE])
        _LOGGER.debug(
            "step user two: continuing with lat %s lon %s post %s",
            self._lat,
            self._lon,
            self._post_code,
        )
        return await self.async_step_user_three()

    async def async_step_user_three(self, user_input=None):
        """Handle the final step of setup."""
        _LOGGER.debug(
            "step user three: continuing with lat %s lon %s post %s",
            self._lat,
            self._lon,
            self._post_code,
        )

        def data_schema(name, station, interval):
            return vol.Schema(
                {
                    vol.Required(
                        CONF_STATION,
                        default=station,
                    ): vol.In(list(self._stations)),
                    vol.Required(
                        CONF_NAME,
                        default=name,
                    ): str,
                    vol.Required(
                        CONF_UPDATE_INTERVAL,
                        default=interval,
                    ): int,
                }
            )

        client = await self.hass.async_add_executor_job(
            meteoSwissClient,
            "No display name",
            self._post_code,
        )

        errors = {}
        if user_input is not None:
            if len(user_input[CONF_NAME].strip()) < 1:
                errors[CONF_NAME] = "empty_name"

            if user_input[CONF_STATION] not in self._stations:
                errors[CONF_STATION] = "invalid_station_name"

            station = self._stations[user_input[CONF_STATION]]

            # check if the station name is 3 character
            if not re.match(r"^\w{3}$", station):
                errors[CONF_STATION] = "invalid_station_name"

            # check if the station name is 3 character
            if user_input[CONF_UPDATE_INTERVAL] < 1:
                errors[CONF_UPDATE_INTERVAL] = "update_interval_too_low"

            # check if the station id is found in stastion list
            stationNameChk = await self.hass.async_add_executor_job(
                client.get_station_name,
                station,
            )
            if stationNameChk is None:
                errors[CONF_STATION] = "invalid_station_id"

            schema = data_schema(
                user_input[CONF_NAME],
                user_input[CONF_STATION],
                user_input[CONF_UPDATE_INTERVAL],
            )
        else:
            station = await self.hass.async_add_executor_job(
                client.get_closest_station, self._lat, self._lon
            )
            if self._stations_map is None:
                self._stations_map = client._allStations
            self._stations = dict(
                ("%s (%s)" % (value["name"], key), key)
                for key, value in self._stations_map.items()
            )
            if station is not None:
                station_name = await self.hass.async_add_executor_job(
                    client.get_station_name, station
                )
            else:
                station_name = ""

            schema = data_schema(
                station_name,
                "%s (%s)" % (station_name, station),
                DEFAULT_UPDATE_INTERVAL,
            )

        if errors or user_input is None:
            return self.async_show_form(
                step_id="user_three", data_schema=schema, errors=errors
            )

        name = user_input[CONF_NAME].strip()
        data = {
            CONF_NAME: name,
            CONF_POSTCODE: self._post_code,
            CONF_STATION: station,
            CONF_UPDATE_INTERVAL: user_input[CONF_UPDATE_INTERVAL],
        }

        _LOGGER.debug(
            "step user three: finishing with %s",
            data,
        )
        return self.async_create_entry(
            title=name,
            data=data,
        )

    async def async_step_import(self, user_input):
        """Import a config entry."""
        return await self.async_step_user(user_input)
