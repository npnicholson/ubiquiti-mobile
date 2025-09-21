"""Constants for ubiquiti_mobile."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "ubiquiti_mobile"

CONF_HOST = "host"

PLATFORMS: list[str] = ["sensor"]  # later you can add switch, binary_sensor, etc.
