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
        
        # database.py
        self.query("""CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_title TEXT,
                quiz_name TEXT,
                quiz_data TEXT,
                start_time TEXT,
                end_time TEXT)""")
        
        # Inside your Database class init or setup method:
        # database.py
        self.query("""CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            quiz_title TEXT,
            score INTEGER,
            total INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        self.conn.commit()

    def query(self, sql, params=()):
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor