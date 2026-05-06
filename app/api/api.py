import requests
import os
from util import log
from util.placeholders import *


class HomeAssistantAPI:
    def __init__(self):
        ### Initialize connection with Home Assistant API
        log.info("Connecting to Home Assistant API...")

        # Retrieve API key from environment variables
        log.info("Retrieving API key from environment variables...")
        self.__API_TOKEN = None
        try:
            self.__API_TOKEN = os.environ["SUPERVISOR_TOKEN"]
            log.toomuchinfo(f"Your API token is: f{self.__API_TOKEN}")
            log.info("Token recieved!")
        except KeyError as e:
            log.error("Token not provided through environment variables. This is expected if you are not running this application within Home Assistant.")
            raise e
        
        # Test connection
        log.info("Testing connection to Home Assistant...")
        conntest = self.__request("/")
        if conntest.status_code != 200:
            log.error(f"Connection test to Home Assistant failed! Error {conntest.status_code}")
            raise ConnectionError()

    # Make an API request. This function call allows extra things to be ran when making API calls like the logger.
    def __request(self, path):
        log.toomuchinfo(f"Sending API request: {path}")
        request = requests.get(
            HASS_API_URL + path,
            headers = {
                'Authorization': f'Bearer {self.__API_TOKEN}',
                'Content-Type': 'application/json'
            }
        )
        try:
            log.toomuchinfo(f"Response: {request.status_code}, {request.body}")
        except AttributeError:
            log.toomuchinfo(f"Response: {request.status_code}, No body")
        return request