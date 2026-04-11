from db import Domain
class DomainLight(Domain):
    # A Light.
    # TODO: We are starting with just keeping track of ON and OFF.
    def __init__(self, state):
        Domain.__init__(self, state)

    def get_insert_command(self, StateHistoryID):
        return """INSERT INTO DomainLightState (StateHistoryID, ON) VALUES ({StateHistoryID}, {self.state})"""