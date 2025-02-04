import sqlite3
import pickle
import KeyGenerator  # Assuming you have a KeyGenerator module

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Create users table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        public_key BLOB NOT NULL,
        private_key BLOB NOT NULL
    )
    ''')

    # Create groups table
    c.execute('''
    CREATE TABLE IF NOT EXISTS groups (
        group_name TEXT PRIMARY KEY,
        private_key BLOB NOT NULL
    )
    ''')

    # Create group_members table
    c.execute('''
    CREATE TABLE IF NOT EXISTS group_members (
        username TEXT,
        group_name TEXT,
        accepted INTEGER DEFAULT 0,
        FOREIGN KEY (username) REFERENCES users (username),
        FOREIGN KEY (group_name) REFERENCES groups (group_name),
        PRIMARY KEY (username, group_name)
    )
    ''')

    # Create notifications table
    c.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        message TEXT,
        FOREIGN KEY (username) REFERENCES users (username)
    )
    ''')

    # Insert premade accounts
    accounts = [
        ("user1", "user1@example.com", "password1"),
        ("user2", "user2@example.com", "password2"),
        ("admin", "admin@example.com", "admin")
    ]
    for username, email, password in accounts:
        if not user_exists(conn, username):
            public_key, private_key = KeyGenerator.generate_keys(username)
            public_key_serialized = pickle.dumps(public_key)
            private_key_serialized = pickle.dumps(private_key)
            c.execute('''
                INSERT INTO users (username, email, password, public_key, private_key)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password, public_key_serialized, private_key_serialized))

    conn.commit()
    conn.close()

def user_exists(conn, username):
    c = conn.cursor()
    result = c.execute('SELECT 1 FROM users WHERE username = ?', (username,)).fetchone()
    return result is not None

if __name__ == '__main__':
    init_db()