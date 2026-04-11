import sqlite3

from .tablecreate import create_tables

class EntityHistoryDatabase:
    def __init__(self):
        # Initialize SQLite3 database
        # This file goes into the container root. It will be preserved upon uninstall, UNLESS the user selects "remove app data"
        self.conn = sqlite3.connect("radded_data_dumper.sqlite3")
        self.cur = self.conn.cursor()

        # Create tables
        create_tables(self.conn, self.cur)