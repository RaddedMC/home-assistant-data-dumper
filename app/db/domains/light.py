from .generic import Domain
class DomainLight(Domain):
    # A Light.
    # TODO: We are starting with just keeping track of ON and OFF.
    def __init__(self, state: bool):
        Domain.__init__(self, state)

    # create_table, which is not an object method and will be called once at runtime to retrieve the SQL to create the table.
    @staticmethod
    def create_table():
        return """
        CREATE TABLE IF NOT EXISTS DomainLightState (
            ID INTEGER PRIMARY KEY,
            StateHistoryID INTEGER NOT NULL,
            isON BOOLEAN NOT NULL,
            FOREIGN KEY (StateHistoryID) REFERENCES EntityHistory(ID)
        );
        """
        
    # add_entry, will be called to retrieve the SQL to add an entry.
    def add_entry(self, state_history_id):
        return f"""
        INSERT INTO DomainLightState (StateHistoryID, isOn) VALUES (
            {state_history_id},
            {self.state}
        );
        """