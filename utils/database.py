import sqlite3
import KeyGenerator
import pickle
from .notification import Notification
import logging

class Database:
    def __init__(self, db_path='app.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def create_tables(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    email TEXT,
                    password TEXT,
                    public_key BLOB,
                    private_key BLOB
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS groups (
                    group_name TEXT PRIMARY KEY,
                    leader TEXT,
                    public_key BLOB,
                    private_key BLOB
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS group_members (
                    group_name TEXT,
                    username TEXT,
                    PRIMARY KEY (group_name, username)
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    message TEXT,
                    group_name TEXT
                )
            ''')

    def add_premade_accounts(self):
        accounts = [
            ("user1", "user1@example.com", "password1"),
            ("user2", "user2@example.com", "password2"),
            ("admin", "admin@example.com", "admin")
        ]
        for username, email, password in accounts:
            if not self.user_exists(username):
                public_key, private_key = KeyGenerator.generate_keys(username)
                public_key_serialized = pickle.dumps(public_key)
                private_key_serialized = pickle.dumps(private_key)
                with self.conn:
                    self.conn.execute('''
                        INSERT INTO users (username, email, password, public_key, private_key)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (username, email, password, public_key_serialized, private_key_serialized))

    def user_exists(self, username):
        with self.conn:
            result = self.conn.execute('''
                SELECT 1 FROM users WHERE username = ?
            ''', (username,)).fetchone()
            return result is not None

    def get_user_info(self, username):
        with self.conn:
            result = self.conn.execute('''
                SELECT username, email FROM users WHERE username = ?
            ''', (username,)).fetchone()
            return result
        
    def get_public_key(self, username):
        with self.conn:
            public_key_serialized = self.conn.execute('''
                SELECT public_key FROM users WHERE username = ?
            ''', (username,)).fetchone()[0]
            return pickle.loads(public_key_serialized)

    def get_private_key(self, username):
        with self.conn:
            private_key_serialized = self.conn.execute('''
                SELECT private_key FROM users WHERE username = ?
            ''', (username,)).fetchone()[0]
            return pickle.loads(private_key_serialized)

    def validate_user(self, username, password):
        with self.conn:
            result = self.conn.execute('''
                SELECT 1 FROM users WHERE username = ? AND password = ?
            ''', (username, password)).fetchone()
            return result is not None

    def add_group(self, leader, group_name):
        public_key, private_key = KeyGenerator.generate_keys(group_name)
        public_key_serialized = pickle.dumps(public_key)
        private_key_serialized = pickle.dumps(private_key)
        with self.conn:
            self.conn.execute('''
                INSERT INTO groups (group_name, leader, public_key, private_key)
                VALUES (?, ?, ?, ?)
            ''', (group_name, leader, public_key_serialized, private_key_serialized))
            self.conn.execute('''
                INSERT INTO group_members (group_name, username)
                VALUES (?, ?)
            ''', (group_name, leader))

    def get_user_groups(self, username):
        with self.conn:
            return [row[0] for row in self.conn.execute('''
                SELECT group_name FROM group_members WHERE username = ?
            ''', (username,)).fetchall()]

    def invite_to_group(self, group_name, username):
        if self.is_user_in_group(group_name, username):
            return False
        with self.conn:
            self.conn.execute('''
                INSERT INTO group_members (group_name, username)
                VALUES (?, ?)
            ''', (group_name, username))
            self.add_notification(username, f"You have been invited to join the group {group_name}")
        return True

    def is_user_in_group(self, group_name, username):
        with self.conn:
            result = self.conn.execute('''
                SELECT 1 FROM group_members WHERE group_name = ? AND username = ?
            ''', (group_name, username)).fetchone()
            return result is not None

    def leave_group(self, group_name, username):
        with self.conn:
            self.conn.execute('''
                DELETE FROM group_members WHERE group_name = ? AND username = ?
            ''', (group_name, username))

    def add_notification(self, username, message, group_name=None):
        with self.conn:
            self.conn.execute('''
                INSERT INTO notifications (username, message, group_name)
                VALUES (?, ?, ?)
            ''', (username, message, group_name))
            last_id = self.conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            logging.debug(f"Notification added with ID: {last_id}")
            return last_id

    def get_notification_by_id(self, notification_id):
        with self.conn:
            result = self.conn.execute('''
                SELECT * FROM notifications WHERE id = ?
            ''', (int(notification_id),)).fetchone()

            if result:
                return dict(result)
            else:
                return None

    def delete_notification(self, notification_id):
        with self.conn:
            logging.debug(f"Deleting notification with id: {notification_id} (type: {type(notification_id)})")
            self.conn.execute('DELETE FROM notifications WHERE id = ?', (int(notification_id),))

    def get_all_notifications(self):
        with self.conn:
            result = self.conn.execute('SELECT * FROM notifications').fetchall()
            return [dict(row) for row in result]

    def accept_invitation(self, group_name, username):
        with self.conn:
            self.conn.execute('''
                UPDATE group_members SET accepted = 1 WHERE group_name = ? AND username = ?
            ''', (group_name, username))
            logging.debug(f"Invitation accepted for user: {username} in group: {group_name}")

    def decline_invitation(self, group_name, username):
        with self.conn:
            self.conn.execute('''
                DELETE FROM group_members WHERE group_name = ? AND username = ?
            ''', (group_name, username))
            logging.debug(f"Invitation declined for user: {username} in group: {group_name}")

    def debug_get_notification_by_id(self, notification_id):
        with self.conn:
            result = self.conn.execute('''
                SELECT * FROM notifications WHERE id = ?
            ''', (int(notification_id),)).fetchone()

            if result:
                # Convert the sqlite3.Row object to a dictionary for better readability
                notification = dict(result)
                print(notification)
            else:
                print(f"No notification found with ID: {notification_id}")