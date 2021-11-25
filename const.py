"""Constants for the HottoH integration."""

DOMAIN = "hottoh"
PLATFORMS: list[str] = ["climate", "sensor", "switch"]
HOTTOH_DEFAULT_HOST = "192.168.4.10"
HOTTOH_DEFAULT_PORT = 5001
HOTTOH_SESSION = "hottoh_session"
CANCEL_STOP = "cancel_stop"
CONF_AWAY_TEMP = "away_temp"
CONF_ECO_TEMP = "eco_temp"
CONF_COMFORT_TEMP = "comfort_temp"

FAN_SPEED_RANGE = (1,6)
