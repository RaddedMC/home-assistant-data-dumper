from flask import Flask
from util import log
from util.placeholders import *
from db.db import EntityHistoryDatabase, StateHistoryEntry, Entity, AutomationTrigger
from db.domains.light import DomainLight
from db.domains.person import DomainPerson
from datetime import datetime
import os
import requests

app = Flask(__name__)

# Routes
@app.route("/")
def hello_world():
    return "Hello world"

# Startup
def main():
    log.info("Starting addon...")

    # Initialize database
    app_db = EntityHistoryDatabase()

    # Connect to Home Assistant API
    # Read bearer token
    log.info("Connecting to Home Assistant API...")
    try:
        API_TOKEN = os.environ["SUPERVISOR_TOKEN"]
        log.toomuchinfo(f"Your API token is: f{API_TOKEN}")
        log.info("Token recieved!")
    except KeyError as e:
        log.error("Did not recieve a supervisor token! This is normal if you aren't running the addon within Home Assistant.")
        raise e
    except Exception as e:
        log.error(f"Something unexpected happened during API connection: {e}")
        raise e

    # Test connection
    test_request = requests.get(HASS_API_URL + "/states/input_boolean.test", headers = {
        'Authorization': f'Bearer {API_TOKEN}'
    })
    print(test_request.content)
    print(test_request.status_code)

### Application startup methods

# python app.py
# This should be called if ran by Home Assistant and is the default launch method.
if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=8067, debug=True) # TODO: Debug probably isn't the best for production!

# flask run
# This should be called if ran by VSCode or just in general via Flask.
main()