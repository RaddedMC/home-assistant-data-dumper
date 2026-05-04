from enum import Enum

DATABASE_VERSION = 1
HASS_API_URL = "http://supervisor/core/api" # If you aren't running the data dumper in Home Assistant, change this to match your instance!

LOG_LEVELS = Enum("Log Levels", [
    ("INSANE", 0), # Warning: This may reveal API keys and SQL statements in your logs!
    ("NORMAL", 1), # Will display verbose "info" messages
    ("STFU", 2)
])
LOG_LEVEL = LOG_LEVELS.NORMAL