from pathlib import Path

from flask import Flask, render_template
from util import log
from util.placeholders import FRONTEND_PATH
from db.db import EntityHistoryDatabase
from api.api import HomeAssistantAPI

# Initialize Flask app
app = Flask(__name__, static_url_path="", static_folder=FRONTEND_PATH)

# Routes
@app.route("/api")
def api_root():
    return "hello world!"

# Startup
def main():
    log.info("Starting addon...")

    # Initialize database
    app_db = EntityHistoryDatabase()

    # Initialize API connection
    hass_api = HomeAssistantAPI()


### Application startup methods

# python app.py
# This should be called if ran by Home Assistant and is the default launch method.
if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=8067, debug=True) # TODO: Debug probably isn't the best for production!

# flask run
# This should be called if ran by VSCode or just in general via Flask.
main()