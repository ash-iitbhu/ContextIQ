import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

from ..config import DB_PATH


class StateDB:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)

    def get_state_memory(self):
        memory = SqliteSaver(self.conn)
        return memory
