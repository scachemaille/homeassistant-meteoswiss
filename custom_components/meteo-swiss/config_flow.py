"""Config flow to configure the Meteo-Swiss integration."""
import logging

import re
import voluptuous as vol
from homeassistant import config_entries
from .const import (
    DOMAIN,
    CONF_FORECAST_NAME,
    CONF_LAT,
    CONF_LON,
    CONF_NAME,
    CONF_POSTCODE,
    CONF_REAL_TIME_NAME,
    CONF_STATION,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
)
from hamsclientfork import meteoSwissClient, StationType
from homeassistant.helpers.issue_registry import IssueSeverity
from homeassistant.helpers import issue_registry as ir
from typing import Any


_LOGGER = logging.getLogger(__name__)


NO_STATION = "No real-time weather station"


class MeteoSwissFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Init FlowHandler."""
        super().__init__()
        self._lat = None
        self._lon = None
        self._post_code = None
        self._forecast_name = None
        self._update_interval = None

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

        def data_schema(postcode, name, interval):
            return vol.Schema(
                {
                    vol.Required(
                        CONF_POSTCODE,
                        default=postcode,
                    ): str,
                    vol.Required(
                        CONF_FORECAST_NAME,
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
            user_input.get(CONF_POSTCODE) if user_input else None,
        )

        errors = {}
        if user_input is not None:
            if not re.match(r"^\d{4}$", str(user_input[CONF_POSTCODE])):
                errors[CONF_POSTCODE] = "invalid_postcode"
            if not str(user_input[CONF_FORECAST_NAME]).strip():
                errors[CONF_FORECAST_NAME] = "real_time_name_empty"
            # check if the station name is 3 character
            if user_input[CONF_UPDATE_INTERVAL] < 1:
                errors[CONF_UPDATE_INTERVAL] = "update_interval_too_low"

            schema = data_schema(
                user_input[CONF_POSTCODE],
                user_input[CONF_FORECAST_NAME],
                user_input[CONF_UPDATE_INTERVAL],
            )
        else:
            geodata = await self.hass.async_add_executor_job(
                client.getGeoData, self._lat, self._lon
            )
            guessed_postal_code = str(
                geodata.get("address", {}).get(
                    "postcode",
                    "",
                )
            )
            guessed_address = " ".join(
                x.strip()
                for x in str(geodata.get("display_name", "",)).split(
                    ","
                )[:3]
            )

            schema = data_schema(
                guessed_postal_code,
                guessed_address,
                DEFAULT_UPDATE_INTERVAL,
            )

        if errors or user_input is None:
            return self.async_show_form(
                step_id="user_two", data_schema=schema, errors=errors
            )

        self._post_code = int(user_input[CONF_POSTCODE])
        self._forecast_name = user_input[CONF_FORECAST_NAME].strip()
        self._update_interval = int(user_input[CONF_UPDATE_INTERVAL])
        _LOGGER.debug(
            "step user two: continuing with lat %s lon %s post %s name %s",
            self._lat,
            self._lon,
            self._post_code,
            self._forecast_name,
        )
        return await self.async_step_user_three()

    async def _get_all_stations_and_closest_one(self, client, lat, lon):
        default_station = await self.hass.async_add_executor_job(
            client.get_closest_station,
            lat,
            lon,
            StationType.WEATHER,
        )
        if default_station:
            default_station_name = await self.hass.async_add_executor_job(
                client.get_station_name, default_station
            )
        else:
            default_station_name = ""
        stations = await self.hass.async_add_executor_job(
            client.get_all_stations,
            StationType.WEATHER,
        )
        all_stations = {NO_STATION: ""}
        all_stations.update(
            {
                "%s (%s)"
                % (
                    value["name"],
                    key,
                ): key
                for key, value in stations.items()
            }
        )
        return default_station, default_station_name, all_stations

    async def async_step_user_three(self, user_input=None):
        """Handle the final step of setup."""
        _LOGGER.debug(
            "step user three: continuing with lat %s lon %s post %s",
            self._lat,
            self._lon,
            self._post_code,
        )

        def data_schema(name, station, stations):
            return vol.Schema(
                {
                    vol.Required(
                        CONF_STATION,
                        default=station,
                    ): vol.In(list(stations)),
                    vol.Optional(
                        CONF_REAL_TIME_NAME,
                        default=name,
                    ): str,
                }
            )

        client = await self.hass.async_add_executor_job(
            meteoSwissClient,
            "No display name",
            self._post_code,
        )

        (
            default_station,
            default_station_name,
            stations,
        ) = await self._get_all_stations_and_closest_one(
            client,
            self._lat,
            self._lon,
        )

        errors = {}
        if user_input is not None:
            if user_input[CONF_STATION] not in stations:
                errors[CONF_STATION] = "invalid_station_name"

            station = stations[user_input[CONF_STATION]]
            if station:
                real_time_name = user_input[CONF_REAL_TIME_NAME].strip()

                if len(real_time_name) < 1:
                    errors[CONF_REAL_TIME_NAME] = "empty_name"

                # check if the station name is 3 character
                if not re.match(r"^\w{3}$", station):
                    errors[CONF_STATION] = "invalid_station_name"

            else:
                station = None
                real_time_name = None

            schema = data_schema(
                user_input[CONF_REAL_TIME_NAME],
                user_input[CONF_STATION],
                stations,
            )
        else:
            if default_station:
                default_station_selection = "%s (%s)" % (
                    default_station_name,
                    default_station,
                )
            else:
                default_station_selection = NO_STATION
            default_station_name = default_station_name or ""

            schema = data_schema(
                default_station_name,
                default_station_selection,
                stations,
            )

        if errors or user_input is None:
            return self.async_show_form(
                step_id="user_three", data_schema=schema, errors=errors
            )

        data = {
            CONF_POSTCODE: self._post_code,
            CONF_FORECAST_NAME: self._forecast_name,
            CONF_UPDATE_INTERVAL: self._update_interval,
        }
        if station and real_time_name:
            data.update(
                {
                    CONF_STATION: station,
                    CONF_REAL_TIME_NAME: real_time_name,
                }
            )

        if real_time_name:
            title = "%s / %s" % (self._forecast_name, real_time_name)
        else:
            title = self._forecast_name

        _LOGGER.debug(
            "step user three: finishing with %s",
            data,
        )
        return self.async_create_entry(
            title=title,
            data=data,
        )

    async def async_step_import(self, import_config: dict[str, Any]):
        """Import a config entry."""
        ir.async_create_issue(
            self.hass,
            DOMAIN,
            "deprecated_yaml",
            is_fixable=False,
            severity=IssueSeverity.WARNING,
            translation_key="deprecated_yaml",
        )

        data = {
            CONF_POSTCODE: import_config[CONF_POSTCODE],
            CONF_UPDATE_INTERVAL: import_config.get(
                CONF_UPDATE_INTERVAL,
                DEFAULT_UPDATE_INTERVAL,
            ),
            CONF_FORECAST_NAME: import_config[CONF_NAME],
        }
        if import_config.get(CONF_STATION):
            data[CONF_STATION] = import_config[CONF_STATION]
            data[CONF_REAL_TIME_NAME] = import_config[CONF_NAME]

        return self.async_create_entry(
            title=data[CONF_NAME],
            data=data,
        )
