import sqlite3

def setup_db(db_file):
    """
    Sets up the SQLite database.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Quotes (
            id INTEGER PRIMARY KEY,
            character TEXT,
            quote TEXT UNIQUE,
            date TEXT,
            sent_to_twitter TEXT,
            sent_to_wordpress TEXT,
            sent_to_whatsapp TEXT
        )
    ''')
    conn.commit()
    return conn, cursor

