class Domain:
    # A generic Domain.
        # State, can be whatever you want! This will be treated as the primary state for the Domain.
        
    def __init__(self, state: any):
        self.state = state

    # create_table, which is not an object method and will be called once at runtime to retrieve the SQL to create the table.
    @staticmethod
    def create_table():
        return ""
    
    # add_entry, will be called to retrieve the SQL to add an entry.
    def add_entry(self, state_history_id):
        return ""