from .log_level import LOG_LEVELS

# Do not change
DATABASE_VERSION = 1

# Change only if you are running OUTSIDE of Home Assistant
HASS_API_URL = "http://supervisor/core/api"

# TODO: Change this to Normal before sharing
# Set your log level
# - INSANE -- Logs all SQL and API queries. Great for development testing, but may LEAK KEYS!
# - NORMAL -- Recommended for all users.
# - SILENT -- Logs only errors and warnings.
LOG_LEVEL = LOG_LEVELS.INSANE

# Change only if you are running OUTSIDE of Home Assistant
BUILT_FRONTEND_PATH = "/frontend/dist"