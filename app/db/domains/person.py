from db import Domain
class DomainLight(Domain):
    # A Person.
    # This domain might also be able to be re-used for Device Tracker.
    # state: The Zone name that the Person is located at
    # isHome: A boolean that represents the Person's location
    def __init__(self, state, isHome):
        Domain.__init__(self, state)
        self.isHome = isHome

    def get_insert_command(self, StateHistoryID):
        return """INSERT INTO DomainPersonState (StateHistoryID, ZoneName, IsHome) VALUES ({StateHistoryID}, {self.state}, {self.isHome})"""