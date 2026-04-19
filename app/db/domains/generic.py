class Domain:
    # A generic Domain.
        # State, can be whatever you want! This will be treated as the primary state for the Domain.
        # get_insert_command, since we will change this for each Domain
        # create_table, which is not an object method and will be called once at runtime to create the relevant domain database tables.
    def __init__(self, state):
        self.state = state

    def get_insert_command(self, StateHistoryID):
        return ""

    @staticmethod
    def create_table():
        return ""