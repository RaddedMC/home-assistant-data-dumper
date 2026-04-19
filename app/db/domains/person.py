from .generic import Domain
class DomainPerson(Domain):
    # A Person.
    # This domain might also be able to be re-used for Device Tracker.
    # state: The Zone name that the Person is located at
    # isHome: A boolean that represents the Person's location
    def __init__(self, state, isHome):
        Domain.__init__(self, state)
        self.isHome = isHome

    def get_insert_command(self, StateHistoryID):
        return """INSERT INTO DomainPersonState (StateHistoryID, ZoneName, IsHome) VALUES ({StateHistoryID}, {self.state}, {self.isHome});"""

    @staticmethod
    def create_table():
        return """CREATE TABLE IF NOT EXISTS DomainPersonState (
            ID INTEGER PRIMARY KEY,
            StateHistoryID INTEGER NOT NULL,
            ZoneName TEXT NOT NULL,
            IsHome BOOLEAN NOT NULL,
            FOREIGN KEY (StateHistoryID) REFERENCES EntityHistory(ID)
        );
        """