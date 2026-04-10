def create_tables(conn, cur):
    def create_event_history_table():
        ### Creates the EventHistory table:
        # ID: A unique identifier.
        # TimeStamp: The date and time that the event occurred.

        cur.execute("""
        CREATE TABLE IF NOT EXISTS EventHistory (
            ID INTEGER PRIMARY KEY,
            TimeStamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            EntityID TEXT NOT NULL,
            EntityArea TEXT,
            AttributeJSON TEXT,
            IsOffline BOOLEAN NOT NULL CHECK (IsOffline IN (0, 1))
        );
        """)

    create_event_history_table()
    conn.commit()