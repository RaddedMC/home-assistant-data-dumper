import sqlite3
from util import log

class EntityHistoryDatabase:
    def __init__(self):
        ### Initialize SQLite3 database
        # This file goes into the container root. It will be preserved upon uninstall, UNLESS the user selects "remove app data"
        log.info("Creating database...")
        self.conn = sqlite3.connect("radded_data_dumper.sqlite3")
        self.cur = self.conn.cursor()

        ### Create top level entity history table
        # ID: A unique identifier for the particular state change.
        # TimeStamp: The date and time that the event occurred.
        # EntityID: A string that contains the ID of the entity which was changed.
            # TODO: Maximum entity ID string length?
        # EntityArea: A string that contains the area name of the entity, if available.
            # TODO: Maximum entity area string length?
        # AttributeJSON: A blob that contains the entity attributes in JSON. These values may be parsed for the subdomain tables.
            # TODO: Maximum entity attributes string length?
        # IsUnavailable: Unavailable entities may not contain the correct domain data. They may also be worth omitting in a dataset.
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS EntityHistory (
            ID INTEGER PRIMARY KEY,
            TimeStamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            EntityID TEXT NOT NULL,
            EntityArea TEXT,
            AttributeJSON TEXT,
            IsUnavailable BOOLEAN NOT NULL
        );
        """)
        
        ### Create automation trigger table
        
        # ID: A unique identifier for the particular automation trigger entry.
        # StateHistoryID: A foreign key that references an EntityHistory item.
        
        # TriggeredByAutomationID: A string that can be null. References the ID of the automation that triggered the state change.
        # TriggeredByAutomationName: A string that can be null. References the name of the automation that triggered the state change.
        
        # TriggeredByEntityID: A string that can be null. References the ID of the entity that triggered the automation that triggered the state change.
        # TriggeredByEntityName: A string that can be null. References the name of the entity that triggered the automation that triggered the state change.
        
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS AutomationTrigger (
            ID INTEGER PRIMARY KEY,
            StateHistoryID NOT NULL FOREIGN KEY,
            TriggeredByAutomationID TEXT,
            TriggeredByAutomationName TEXT,
            TriggeredByEntityID TEXT,
            TriggeredByEntityName TEXT
        );
        """)

        ### Commit all of the above
        self.conn.commit()

class EntityHistoryEntry:
    # An entry in the Entity History database.
        # Timestamp, self explanatory
        # Entity, see below
        # Domain, see below
        # Automation trigger, or none if not applicable
    def __init__(self, timestamp, entity, domain, automation_trigger = None):
        self.timestamp = timestamp
        self.entity = entity
        self.domain = domain
        self.automation_trigger = automation_trigger

class Entity:
    # An entity.
        # Entity ID
        # Entity Area name
        # List of attributes as JSON
        # Boolean, true if entity is marked as "unavailable"
    def __init__(self, entity_id, entity_area, attributes, unavailable):
        self.entity_id = entity_id
        self.entity_area = entity_area
        self.attributes = attributes
        self.unavailable = unavailable

class DomainGeneric:
    # A generic Domain.
        # State, can be whatever you want! This will be treated as the primary state for the Domain.
        # get_insert_command, since we will change this for each Domain
    def __init__(self, state):
        self.state = state

    def get_insert_command(self, StateHistoryID):
        return ""

class AutomationTrigger:
    # An automation trigger. In Home Assistant, this is read as "X set to state Y triggered by automation A triggered by state of B"
    def __init__(self, triggered_by_automation_id = None, triggered_by_automation_name = None, triggered_by_entity_id = None, triggered_by_entity_name = None):
        self.triggered_by_automation_id = triggered_by_automation_id
        self.triggered_by_automation_name = triggered_by_automation_name
        self.triggered_by_entity_id = triggered_by_entity_id
        self.triggered_by_entity_name = triggered_by_entity_name
        

# Log flow:
# Create EntityHistoryEntry
    # Create Entity
    # Create Domain
    # Create AutomationTrigger