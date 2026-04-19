from .generic import Domain
class DomainLight(Domain):
    # A Light.
    # TODO: We are starting with just keeping track of ON and OFF.
    def __init__(self, state):
        Domain.__init__(self, state)

    def get_insert_command(self, StateHistoryID):
        return """INSERT INTO DomainLightState (StateHistoryID, ON) VALUES ({StateHistoryID}, {self.state});"""

    @staticmethod
    def create_table():
        return """CREATE TABLE IF NOT EXISTS DomainLightState (
            ID INTEGER PRIMARY KEY,
            StateHistoryID INTEGER NOT NULL,
            isON BOOLEAN NOT NULL,
            FOREIGN KEY (StateHistoryID) REFERENCES EntityHistory(ID)
        );
        """