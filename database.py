import sqlite3

class Database:
    def __init__(self, db_name="school_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Students Table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            firstname TEXT, lastname TEXT, 
            section TEXT, username TEXT UNIQUE, password TEXT)''')
        
        # Schedules Table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_title TEXT,
            quiz_name TEXT,
            quiz_data TEXT,
            pass_code TEXT,
            start_time TEXT,
            end_time TEXT)''')
        self.conn.commit()

    def query(self, sql, params=()):
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor