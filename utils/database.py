import sqlite3
import KeyGenerator
import pickle  # Import pickle for serialization

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("app.db", check_same_thread=False)  # Add check_same_thread=False
        self.create_tables()
        self.add_premade_accounts()

    def create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    email TEXT,
                    password TEXT,
                    public_key BLOB,
                    private_key BLOB
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    group_name TEXT PRIMARY KEY,
                    leader TEXT,
                    public_key BLOB,
                    private_key BLOB
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS group_members (
                    group_name TEXT,
                    username TEXT,
                    PRIMARY KEY (group_name, username)
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    username TEXT,
                    notification TEXT
                )
            """)

    def add_premade_accounts(self):
        accounts = [
            ("user1", "user1@example.com", "password1"),
            ("user2", "user2@example.com", "password2"),
            ("admin", "admin@example.com", "admin")
        ]
        for username, email, password in accounts:
            if not self.user_exists(username):
                public_key, private_key = KeyGenerator.main()
                public_key_serialized = pickle.dumps(public_key)  # Serialize the public key
                private_key_serialized = pickle.dumps(private_key)  # Serialize the private key
                with self.conn:
                    self.conn.execute("""
                        INSERT INTO users (username, email, password, public_key, private_key)
                        VALUES (?, ?, ?, ?, ?)
                    """, (username, email, password, public_key_serialized, private_key_serialized))

    def user_exists(self, username):
        with self.conn:
            result = self.conn.execute("""
                SELECT 1 FROM users WHERE username = ?
            """, (username,)).fetchone()
            return result is not None

    def get_user_info(self, username):
        with self.conn:
            result = self.conn.execute("""
                SELECT username, email FROM users WHERE username = ?
            """, (username,)).fetchone()
            return result
        
    def get_public_key(self, username):
        with self.conn:
            public_key_serialized = self.conn.execute("""
                SELECT public_key FROM users WHERE username = ?
            """, (username,)).fetchone()[0]
            return pickle.loads(public_key_serialized)  # Deserialize the public key

    def get_private_key(self, username):
        with self.conn:
            private_key_serialized = self.conn.execute("""
                SELECT private_key FROM users WHERE username = ?
            """, (username,)).fetchone()[0]
            return pickle.loads(private_key_serialized)  # Deserialize the private key

    def validate_user(self, username, password):
        with self.conn:
            result = self.conn.execute("""
                SELECT 1 FROM users WHERE username = ? AND password = ?
            """, (username, password)).fetchone()
            return result is not None

    def add_group(self, leader, group_name):
        public_key, private_key = KeyGenerator.main()
        public_key_serialized = pickle.dumps(public_key)  # Serialize the public key
        private_key_serialized = pickle.dumps(private_key)  # Serialize the private key
        with self.conn:
            self.conn.execute("""
                INSERT INTO groups (group_name, leader, public_key, private_key)
                VALUES (?, ?, ?, ?)
            """, (group_name, leader, public_key_serialized, private_key_serialized))
            self.conn.execute("""
                INSERT INTO group_members (group_name, username)
                VALUES (?, ?)
            """, (group_name, leader))

    def get_user_groups(self, username):
        with self.conn:
            return [row[0] for row in self.conn.execute("""
                SELECT group_name FROM group_members WHERE username = ?
            """, (username,)).fetchall()]

    def invite_to_group(self, group_name, username):
        with self.conn:
            self.conn.execute("""
                INSERT INTO group_members (group_name, username)
                VALUES (?, ?)
            """, (group_name, username))
            self.add_notification(username, f"You have been invited to join the group {group_name}")

    def kick_from_group(self, group_name, username):
        with self.conn:
            self.conn.execute("""
                DELETE FROM group_members WHERE group_name = ? AND username = ?
            """, (group_name, username))
            self.add_notification(username, f"You have been kicked from the group {group_name}")

    def add_notification(self, username, notification):
        with self.conn:
            self.conn.execute("""
                INSERT INTO notifications (username, notification)
                VALUES (?, ?)
            """, (username, notification))

    def get_notifications(self, username):
        with self.conn:
            return [row[0] for row in self.conn.execute("""
                SELECT notification FROM notifications WHERE username = ?
            """, (username,)).fetchall()]