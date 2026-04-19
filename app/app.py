from flask import Flask
from util import log
from db.db import EntityHistoryDatabase

app = Flask(__name__)

# Routes
@app.route("/")
def hello_world():
    return "Hello world"

# Startup
def main():
    log.info("Starting addon...")
    app_db = EntityHistoryDatabase()
    

### Application startup methods

# python app.py
# This should be called if ran by Home Assistant and is the default launch method.
if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=8067, debug=True) # TODO: Debug probably isn't the best for production!
    
# flask run
# This should be called if ran by VSCode or just in general via Flask.
main()