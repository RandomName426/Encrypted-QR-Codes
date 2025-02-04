import sqlite3
import KeyGenerator
import pickle
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
                    accepted INTEGER DEFAULT 0,
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
            user = self.conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            groups = self.conn.execute('SELECT group_name FROM group_members WHERE username = ?', (username,)).fetchall()
            return {'username': user['username'], 'email': user['email'], 'groups': [g['group_name'] for g in groups]}


    def get_public_key(self, username):
        with self.conn:
            public_key_serialized = self.conn.execute('''
                SELECT public_key FROM users WHERE username = ?
            ''', (username,)).fetchone()[0]
            return pickle.loads(public_key_serialized)

    def get_private_key(self, username):
        with self.conn:
            private_key_serialized = self.conn.execute('SELECT private_key FROM users WHERE username = ?', (username,)).fetchone()[0]
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
                INSERT INTO group_members (group_name, username, accepted)
                VALUES (?, ?, 1)
            ''', (group_name, leader))

    def group_exists(self, group_name):
        with self.conn:
            result = self.conn.execute('SELECT 1 FROM groups WHERE group_name = ?', (group_name,)).fetchone()
            return result is not None

    def get_user_groups(self, username):
        with self.conn:
            return [row[0] for row in self.conn.execute('''
                SELECT group_name FROM group_members WHERE username = ? AND accepted = 1
            ''', (username,)).fetchall()]

    def get_all_groups(self):
        with self.conn:
            return [row['group_name'] for row in self.conn.execute('''
                SELECT group_name FROM groups
            ''').fetchall()]

    def invite_to_group(self, group_name, username):
        if self.is_user_in_group(group_name, username):
            return False
        with self.conn:
            self.conn.execute('''
                INSERT INTO group_members (group_name, username, accepted)
                VALUES (?, ?, 0)
            ''', (group_name, username))
            self.add_notification(username, f"You have been invited to join the group {group_name}", group_name)
        return True

    def is_user_in_group(self, username, group_name):
        with self.conn:
            result = self.conn.execute('''
                SELECT 1 FROM group_members WHERE group_name = ? AND username = ?
            ''', (group_name, username)).fetchone()
            logging.debug(f"Checking if {username} is in group {group_name}: {'Yes' if result else 'No'}")
            return result is not None

    def leave_group(self, group_name, username):
        with self.conn:
            self.conn.execute('''
                DELETE FROM group_members WHERE group_name = ? AND username = ?
            ''', (group_name, username))

    def get_group_public_key(self, group_name):
        with self.conn:
            public_key_serialized = self.conn.execute('''
                SELECT public_key FROM groups WHERE group_name = ?
            ''', (group_name,)).fetchone()[0]
            return pickle.loads(public_key_serialized)

    def get_group_private_key(self, group_name):
        with self.conn:
            private_key_serialized = self.conn.execute('SELECT private_key FROM groups WHERE group_name = ?', (group_name,)).fetchone()[0]
            return pickle.loads(private_key_serialized)

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
            return dict(result) if result else None

    def delete_notification(self, notification_id):
        with self.conn:
            logging.debug(f"Deleting notification with id: {notification_id} (type: {type(notification_id)})")
            self.conn.execute('DELETE FROM notifications WHERE id = ?', (int(notification_id),))

    def get_all_notifications(self):
        with self.conn:
            result = self.conn.execute('SELECT * FROM notifications').fetchall()
            return [dict(row) for row in result]

    def get_user_notifications(self, username):
        with self.conn:
            result = self.conn.execute('''
                SELECT * FROM notifications WHERE username = ?
            ''', (username,)).fetchall()
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

    def delete_empty_groups(self):
        with self.conn:
            # Find groups with no members
            empty_groups = self.conn.execute('''
                SELECT group_name FROM groups
                WHERE group_name NOT IN (SELECT DISTINCT group_name FROM group_members)
            ''').fetchall()

            # Delete empty groups
            for group in empty_groups:
                self.conn.execute('DELETE FROM groups WHERE group_name = ?', (group['group_name'],))
                logging.debug(f"Deleted empty group: {group['group_name']}")