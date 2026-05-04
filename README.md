# Radded's Home Assistant Data Dumper

## Description

A robust app to dump the time-series Entity state data from Home Assistant. This application will pull all history that is currently available, and routinely poll as states change. This will create a large and detailed dataset that can be used for training Machine Learning models.

## Features

- On first installation, the app will collect all entity state history that is currently stored on the Home Assistant instance.
- For a user-configurable interval, the app will regularly collect new entity state history.
- This data is stored **locally and privately** on the instance in an SQLite database.
- The user can then choose which data to download from the addon, based on the following filters. Data will be exported as a `.sqlite3` database file.
  - Date and Time range
  - Entity domains (whitelist, blacklist)
  - Entity areas (whitelist, blacklist)
  - Entities (whitelist, blacklist)

## installation

### Existing HA instance:

- Clone this repo into your Home Assistant `/root/addons` folder
- In Home Assistant, go to Settings > Apps (formerly Addons) > Install App > Local Apps and install "Radded's Home Assistant Data Dumper
- You can also do development using VSCode Remote SSH

### TESTING

#### Devcontainer (for local development)

- Dependencies: Docker, Python, Git
- Clone this repo to your system
- Open it with Visual Studio Code
- Run the Dev Container (you may be prompted to install a few extensions)
- Once the container is running, go to Terminal -> Run Task -> Start Home Assistant

#### Outside of HA (Useful for testing database, webserver)

- Clone this repo to your system
- Create a new virtual environment with `python -m venv .venv`
- Activate the virtual environment with `source .venv/bin/activate`
- Install the dependencies with `pip install -r requirements.txt`
- Change directory into the `app` folder
- Run `flask run` and enjoy!

## Database

- `StateHistory`: A table that lists the changes to all Entities
  - WILL FOCUS ON THIS FIRST
  - `ID NOT NULL UNIQUE INTEGER`:
    - some unique identifier
  - `TimeStamp NOT NULL INTEGER`:
    - The data and time that the state change happened
  - `EntityID NOT NULL STR LENGTH X`:
    - The unique ID of the entity in Home Assistant
    - TODO: What is Home Assistant's maximum entity ID length?
  - `EntityArea NULLABLE STR LENGTH X`:
    - The area that the entity belongs to
    - TODO: What is the maximum area name length in Home Assistant?
  - `AttributeJSON NULLABLE STR LENGTH X`
    - The additional Attributes that may be on any particular entity
    - TODO: Do we need this? How long should this be?
  - `IsOffline BOOLEAN NOT NULL`
    - If the device is Unavailable, Offline, or Unknown, we will treat it as Offline.

- `AutomationTrigger`: A table, linking to `StateHistory`, that shows which entities and automations triggered a particular entity state change.
  - `ID NOT NULL UNIQUE INTEGER`:
    - some unique identifier
  - `StateHistoryID NOT NULL FOREIGN KEY StateHistory.ID`:
    - Foreign Key to StateHistoryID
  - `TriggereSdByAutomationID NULLABLE STR`:
    - The entity of the automation that triggered this change, if applicable.
  - `TriggeredByEntityName NULLABLE STR`:
    - The name of the entity that triggered the automation that triggered this change, if applicable.

For the below tables, only ONE of these tables should be linked to any given row of `StateHistoryID`.

- `DomainLightState`: A table that shows the specific information for a Light entity, linking to `StateHistory`.
  - WILL FOCUS ON THIS FIRST
  - `ID NOT NULL UNIQUE INTEGER`:
    - some unique identifier
  - `StateHistoryID NOT NULL FOREIGN KEY StateHistory.ID`:
    - Foreign Key to StateHistoryID
  - `ON BOOL NOT NULL`:
    - A boolean to identify whether the light is on or off
  - TODO: Add more

- `DomainPersonState`:
  - WILL FOCUS ON THIS FIRST. This is not a recognized domain in the developer docs, despite their being an entity ID class for it. I don't quite understand this.
  - `ID NOT NULL UNIQUE INTEGER`:
    - some unique identifier
  - `StateHistoryID NOT NULL FOREIGN KEY StateHistory.ID`:
    - Foreign Key to StateHistoryID
  - `ZoneName NOT NULL STR`:
    - A string that represents the name of the Zone that the person is located at.
    - Most users will likely be "Home" or "Away", but this allows the flexibility of multiple Zones.
  - `IsHome BOOL NOT NULL`:
    - A boolean to identify whether the person is Home or somewhere else.

- `DomainBinarySensorState`:
  - WILL FOCUS ON THIS FIRST
  - `ID NOT NULL UNIQUE INTEGER`:
    - some unique identifier
  - `StateHistoryID NOT NULL FOREIGN KEY StateHistory.ID`:
    - Foreign Key to StateHistoryID
  - `ON BOOL NOT NULL`:
    - A boolean to identify whether the binary sensor is on or off
  - `DeviceClass STR NULLABLE`:
    - A string that defines the Device Class of the binary sensor. To be used later!

- `DomainSwitchState`:
  - `ID NOT NULL UNIQUE INTEGER`:
    - some unique identifier
  - `StateHistoryID NOT NULL FOREIGN KEY StateHistory.ID`:
    - Foreign Key to StateHistoryID
  - `ON BOOL NOT NULL`:
    - A boolean to identify whether the switch is on or off

- `DomainLockState`:
  - `ID NOT NULL UNIQUE INTEGER`:
    - some unique identifier
  - `StateHistoryID NOT NULL FOREIGN KEY StateHistory.ID`:
    - Foreign Key to StateHistoryID
  - `State ENUM NOT NULL`:
    - Classes: `Jammed, Open, Opening, Locked, Locking, Unlocked, Unlocking`

- `DomainVacuumState`:
  - `ID NOT NULL UNIQUE INTEGER`:
    - some unique identifier
  - `StateHistoryID NOT NULL FOREIGN KEY StateHistory.ID`:
    - Foreign Key to StateHistoryID
  - `State ENUM NOT NULL`:
    - Classes: `Cleaning, Docked, Error, Idle, Paused, Returning`

- `DomainFanState`:
  - `ID NOT NULL UNIQUE INTEGER`:
    - some unique identifier
  - `StateHistoryID NOT NULL FOREIGN KEY StateHistory.ID`:
    - Foreign Key to StateHistoryID
  - `ON BOOL NOT NULL`:
    - A boolean to identify whether the fan is on or off

- `DomainNumericSensorState`:
  - This table represents Sensor entities which have a numeric value.
  - The value is determined by the existence of the attribute `unit_of_measurement`.
  - `ID NOT NULL UNIQUE INTEGER`:
    - some unique identifier
  - `StateHistoryID NOT NULL FOREIGN KEY StateHistory.ID`:
    - Foreign Key to StateHistoryID
  - `Value FLOAT NOT NULL`:
    - The current value of the sensor
  - `UnitOfMeasurement STR NOT NULL LENGTH X`:
    - TODO: How long is the unit of measurement string?

- `DomainMediaPlayerState`:
  - `ID NOT NULL UNIQUE INTEGER`:
    - some unique identifier
  - `StateHistoryID NOT NULL FOREIGN KEY StateHistory.ID`:
    - Foreign Key to StateHistoryID
  - `PlayState NOT NULL ENUM`:
    - Classes: `Off, On, Idle, Playing, Paused, Buffering`
