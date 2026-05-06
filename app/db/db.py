import sqlite3
from util import log
from util import placeholders
from . import domains
import sys
from .domains.generic import Domain
import json

class EntityHistoryDatabase:
    def __init__(self):
        ### Initialize SQLite3 database
        # This file goes into the container root. It will be preserved upon uninstall, UNLESS the user selects "remove app data"
        log.info("Creating database...")
        self.conn = sqlite3.connect("radded_data_dumper.sqlite3")
        self.cur = self.conn.cursor()
        
        self.__send_query("""
        CREATE TABLE IF NOT EXISTS DatadumperMigrations (
            version INT PRIMARY KEY,
            migratedAt DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        ### Check database version
        local_db_version = self.__send_query("""
        SELECT MAX(version) FROM DatadumperMigrations;
        """).fetchone()[0]
        
        # First time launch
        if local_db_version is None:
            log.info("Detected first time launch")
            self.__send_query("""
            INSERT INTO DatadumperMigrations (version) VALUES (1);
            """)
        elif local_db_version == placeholders.DATABASE_VERSION:
            log.info("Database version unchanged, skipping creation.")
            return
        elif local_db_version > placeholders.DATABASE_VERSION:
            log.error(f"Database is newer than application! Installed: {local_db_version}, Expected: {placeholders.DATABASE_VERSION}")
            sys.exit(1)
        elif local_db_version < placeholders.DATABASE_VERSION:
            log.error(f"Database is older than application! Please perform a migration before continuing. Installed: {local_db_version}, Expected: {placeholders.DATABASE_VERSION}")
            sys.exit(1)


        ### Create top level Entity History table
        self.__send_query(StateHistoryEntry.create_table())
        log.info("-> Created EntityHistory table")


        ### Create automation trigger table
        self.__send_query(AutomationTrigger.create_table())
        log.info("-> Created AutomationTrigger table")


        ### Create tables for all domains
        # Get the list of names of modules
        domain_module_names = domains.list_domains()
        domain_modules = []
        # Get the modules
        for module_name in domain_module_names:
            # Don't call the generic domain
            if module_name == "generic":
                continue
            
            domain_modules.append((module_name, sys.modules["db.domains."+module_name]))
        
        # Get the classes from the modules (save them)
        self.domain_classes = [('Domain' + module_name.title(), getattr(module, 'Domain' + module_name.title())) for module_name, module in domain_modules]
        
        # Use the create_table from each class to create a matching table in the database
        for domain_name, domain_class in self.domain_classes:
            if hasattr(domain_class, 'create_table'):
                print(domain_class.create_table())
                self.__send_query(domain_class.create_table())
                log.info(f"-> Created {domain_name} table")
            else:
                log.info(f"-> Error! {domain_name} does not have a create_table function.")
    
        ### Commit all of the above
        self.conn.commit()
        
    def __send_query(self, query):
        log.toomuchinfo(f"Sending SQL: {query}")
        return self.cur.execute(query)

    def insert_complete_entry(self, state_history_entry):
        # Start by inserting the StateHistoryEntry by itself, to get its ID
        self.__send_query(state_history_entry.add_entry())
        state_history_id = self.cur.lastrowid
        
        # Now insert the domain and automation trigger
        self.__send_query(state_history_entry.domain.add_entry(state_history_id))
        
        if state_history_entry.automation_trigger:
            self.__send_query(state_history_entry.automation_trigger.add_entry(state_history_id))

        # Commit all queries
        self.conn.commit()


class Entity:
    # An entity.
        # Entity ID
        # Entity Area name
        # List of attributes as JSON
        # Boolean, true if entity is marked as "unavailable"
    def __init__(self, entity_id: str, entity_area: str, attributes: any, unavailable: bool):
        self.entity_id = entity_id
        self.entity_area = entity_area
        self.attributes = attributes
        self.unavailable = unavailable

# TODO: Include data for "X set to state Y by action?"

class AutomationTrigger:
    # An automation trigger. In Home Assistant, this is read as "X set to state Y triggered by automation A triggered by state of B"
    def __init__(self, triggered_by_automation_id:str = None, triggered_by_automation_name:str = None, triggered_by_entity_id:str = None, triggered_by_entity_name:str = None):
        self.triggered_by_automation_id = triggered_by_automation_id
        self.triggered_by_automation_name = triggered_by_automation_name
        self.triggered_by_entity_id = triggered_by_entity_id
        self.triggered_by_entity_name = triggered_by_entity_name
        
    @staticmethod
    def create_table():
        
        # ID: A unique identifier for the particular automation trigger entry.
        # StateHistoryID: A foreign key that references an EntityHistory item.

        # TriggeredByAutomationID: A string that can be null. References the ID of the automation that triggered the state change.
        # TriggeredByAutomationName: A string that can be null. References the name of the automation that triggered the state change.

        # TriggeredByEntityID: A string that can be null. References the ID of the entity that triggered the automation that triggered the state change.
        # TriggeredByEntityName: A string that can be null. References the name of the entity that triggered the automation that triggered the state change.
        
        ### Create automation trigger table
        return """
        CREATE TABLE IF NOT EXISTS AutomationTrigger (
            ID INTEGER PRIMARY KEY,
            StateHistoryID INTEGER NOT NULL,
            TriggeredByAutomationID TEXT,
            TriggeredByAutomationName TEXT,
            TriggeredByEntityID TEXT,
            TriggeredByEntityName TEXT,
            FOREIGN KEY (StateHistoryID) REFERENCES EntityHistory(ID)
        );
        """
        
    # Retrieves the SQL to create an entry
    def add_entry(self, state_history_id):
        return f"""
        INSERT INTO AutomationTrigger (StateHistoryID, TriggeredByAutomationID, TriggeredByAutomationName, TriggeredByEntityID, TriggeredByEntityName) VALUES (
            {state_history_id},
            '{self.triggered_by_automation_id}',
            '{self.triggered_by_automation_name}',
            '{self.triggered_by_entity_id}',
            '{self.triggered_by_entity_name}'
        );
        """


class StateHistoryEntry:
    # An entry in the Entity History database.
        # Timestamp, self explanatory
        # Entity, see below
        # Domain, see below
        # Automation trigger, or none if not applicable
    def __init__(self, timestamp: str, entity: Entity, domain: Domain, automation_trigger: AutomationTrigger = None):
        self.timestamp = timestamp
        self.entity = entity
        self.domain = domain
        self.automation_trigger = automation_trigger
        
    @staticmethod
    def create_table():
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
        return """
        CREATE TABLE IF NOT EXISTS EntityHistory (
            ID INTEGER PRIMARY KEY,
            TimeStamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            EntityID TEXT NOT NULL,
            EntityArea TEXT,
            AttributeJSON TEXT,
            IsUnavailable BOOLEAN NOT NULL
        );
        """

    # Retrieves the SQL to create an entry
    # Adding an actual entry needs to be done through the database, since it needs to reference the ID of this Entry
    def add_entry(self):
        return f"""
        INSERT INTO EntityHistory (EntityID, EntityArea, AttributeJSON, IsUnavailable) VALUES (
            '{self.entity.entity_id}',
            '{self.entity.entity_area}',
            '{json.dumps(self.entity.attributes)}',
            {self.entity.unavailable}
        );
        """