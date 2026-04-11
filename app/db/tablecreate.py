from util import log
import sqlite3

def create_tables(conn, cur):
    def create_event_history_table():
        ### Creates the EventHistory table:
        # ID: A unique identifier.
        # TimeStamp: The date and time that the event occurred.

        # cur.execute("""
        # CREATE TABLE IF NOT EXISTS EventHistory (
        #     ID INTEGER PRIMARY KEY,
        #     TimeStamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        #     EntityID TEXT NOT NULL,
        #     EntityArea TEXT,
        #     AttributeJSON TEXT,
        #     IsOffline BOOLEAN NOT NULL CHECK (IsOffline IN (0, 1))
        # );
        # """)

        # DB Testing -- Does the file persist?
        cur.execute("""
        CREATE TABLE IF NOT EXISTS testTable (
            ID INTEGER PRIMARY KEY
        );
        """)

        log.info("Created TESTING table!")

        res = cur.execute("SELECT id FROM testTable;")
        log.info("Result from SELECT id FROM testTable: " + str(res.fetchone()))

        try:
            cur.execute("INSERT INTO testTable VALUES(67);")
            log.info("Created test value!")
        except sqlite3.IntegrityError:
            log.info("Seems that the test data already exists!")

    create_event_history_table()
    conn.commit()