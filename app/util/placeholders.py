from .log_level import LOG_LEVELS

### DATABASE ###
# Database version. Used for migrations.
DATABASE_VERSION = 1 # DO NOT CHANGE UNLESS MIGRATIONS ARE NOT WORKING


### ENVIRONMENT ###
# These settings should not be changed unless you are running outside of Home Assistant.

# The URL that Data Dumper calls to get data from Home Assistant.
HASS_API_URL = "http://supervisor/core/api"
# The location of the Frontend static files.
BUILT_FRONTEND_PATH = "/frontend/dist"


### LOGGING ###
# TODO: Change this to Normal before sharing
# Set your log level
# - INSANE -- Logs all SQL and API queries. Great for development testing, but may LEAK KEYS!
# - NORMAL -- Recommended for all users.
# - SILENT -- Logs only errors and warnings.
LOG_LEVEL = LOG_LEVELS.INSANE

