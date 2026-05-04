from flask import Flask
from util import log
from db.db import EntityHistoryDatabase, StateHistoryEntry, Entity, AutomationTrigger
from db.domains.light import DomainLight
from db.domains.person import DomainPerson
from datetime import datetime
import os

app = Flask(__name__)

# Routes
@app.route("/")
def hello_world():
    return "Hello world"

# Startup
def main():
    log.info("Starting addon...")
    # app_db = EntityHistoryDatabase()

    # Create test data
    # log.info("Creating test data...")
    # app_db.insert_complete_entry(
    #     StateHistoryEntry(
    #         datetime.now(),
    #         Entity(
    #             "light.test_light",
    #             "Test Room",
    #             {
    #                 "test": True
    #             },
    #             False
    #         ),
    #         DomainLight(
    #             True
    #         ),
    #         AutomationTrigger(
    #             "automation.test_light_automation",
    #             "Test Light Automation",
    #             "button.test",
    #             "Test Button"
    #         )
    #     )
    # )

    # Connect to Home Assistant API
    # Read bearer token
    log.info("Connecting to Home Assistant API...")
    try:
        API_TOKEN = os.environ["SUPERVISOR_TOKEN"]
        log.info("Token recieved!")
    except KeyError:
        log.warning("Did not recieve a supervisor token! This is normal if you aren't running the addon within Home Assistant.")
    except Exception as e:
        log.error(f"Some weird bullshit happened: {e}")

    # Test connection



### Application startup methods

# python app.py
# This should be called if ran by Home Assistant and is the default launch method.
if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=8067, debug=True) # TODO: Debug probably isn't the best for production!

# flask run
# This should be called if ran by VSCode or just in general via Flask.
main()