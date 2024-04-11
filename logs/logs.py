import os
import sqlite3
import json
from datetime import datetime, timedelta


class Logs:
    def __init__(self):
        db_file = os.path.join(os.path.dirname(__file__), 'requests.db')
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.last_cleanup_time = self.get_last_cleanup_time()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS logs
                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                request TEXT,
                                response TEXT,
                                session TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS cleanup_info
                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                last_cleanup_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        self.conn.commit()

    def add_log(self, request, response, session=None):
        self.check_and_cleanup_logs()
        self.cursor.execute("INSERT INTO logs (request, response, session) VALUES (?, ?, ?)",
                            (json.dumps(request), json.dumps(response), json.dumps(session)))
        self.conn.commit()

    def get_log_by_id(self, log_id):
        self.cursor.execute("SELECT request, response, session FROM logs WHERE id = ?", (log_id,))
        row = self.cursor.fetchone()
        if row:
            return json.loads(row[0]), json.loads(row[1]), json.loads(row[2])
        else:
            return None, None, None

    def get_last_cleanup_time(self):
        self.cursor.execute("SELECT last_cleanup_time FROM cleanup_info ORDER BY id DESC LIMIT 1")
        row = self.cursor.fetchone()
        if row:
            return datetime.fromisoformat(row[0])
        else:
            return datetime.now()

    def set_last_cleanup_time(self, timestamp):
        self.cursor.execute("INSERT INTO cleanup_info (last_cleanup_time) VALUES (?)", (timestamp,))
        self.conn.commit()

    def cleanup_database(self):
        self.cursor.execute("DELETE FROM logs")
        self.conn.commit()

    def close(self):
        self.conn.close()

    def check_and_cleanup_logs(self):
        current_time = datetime.now()
        if current_time - self.last_cleanup_time >= timedelta(weeks=1):
            self.cleanup_database()
            self.last_cleanup_time = current_time

