from .generic import Domain
class DomainPerson(Domain):
    # A Person.
    # This domain might also be able to be re-used for Device Tracker.
    # state: The Zone name that the Person is located at
    # isHome: A boolean that represents the Person's location
    def __init__(self, state, isHome):
        Domain.__init__(self, state)
        self.isHome = isHome

    # create_table, which is not an object method and will be called once at runtime to retrieve the SQL to create the table.
    @staticmethod
    def create_table():
        return """
        CREATE TABLE IF NOT EXISTS DomainPersonState (
            ID INTEGER PRIMARY KEY,
            StateHistoryID INTEGER NOT NULL,
            ZoneName TEXT NOT NULL,
            IsHome BOOLEAN NOT NULL,
            FOREIGN KEY (StateHistoryID) REFERENCES EntityHistory(ID)
        );
        """
    
    # add_entry, will be called to retrieve the SQL to add an entry.
    def add_entry(self, state_history_id):
        return f"""
        INSERT INTO DomainPersonState (StateHistoryID, ZoneName, IsHome) VALUES (
            {state_history_id},
            {self.state},
            {self.isHome}
        );
        """