import sqlite3
from tablecreate import create_tables

class EntityHistoryDatabase:
    def __init__():
        # Initialize SQLite3 database
        self.conn = sqlite3.connect("radded_data_dumper.sqlite3")
        self.cur = self.conn.cursor()

        # Create tables
        create_tables(conn, cur)