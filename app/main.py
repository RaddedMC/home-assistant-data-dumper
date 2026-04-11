from flask import Flask
from util import log
from db.db import EntityHistoryDatabase

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Hello world"

if __name__ == "__main__":
    log.info("Starting addon...")
    app_db = EntityHistoryDatabase()

    app.run(host="0.0.0.0", port=8067, debug=True) # TODO: I suspect debug mode isn't great for production use