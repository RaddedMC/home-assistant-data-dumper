from flask import Flask
from util import log
from db.db import EntityHistoryDatabase, StateHistoryEntry, Entity, AutomationTrigger
from db.domains.light import DomainLight
from db.domains.person import DomainPerson
from datetime import datetime

app = Flask(__name__)

# Routes
@app.route("/")
def hello_world():
    return "Hello world"

# Startup
def main():
    log.info("Starting addon...")
    app_db = EntityHistoryDatabase()

    # Create test data
    log.info("Creating test data...")
    app_db.insert_complete_entry(
        StateHistoryEntry(
            datetime.now(),
            Entity(
                "light.test_light",
                "Test Room",
                {
                    "test": True
                },
                False
            ),
            DomainLight(
                True
            ),
            AutomationTrigger(
                "automation.test_light_automation",
                "Test Light Automation",
                "button.test",
                "Test Button"
            )
        )
    )
    

### Application startup methods

# python app.py
# This should be called if ran by Home Assistant and is the default launch method.
if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=8067, debug=True) # TODO: Debug probably isn't the best for production!
    
# flask run
# This should be called if ran by VSCode or just in general via Flask.
main()