import sqlite3
import pickle
import logging
import KeyGenerator  # Assuming you have a KeyGenerator module

class Database:
    def __init__(self, db_file='database.db'):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.init_db()

    def init_db(self):
        with self.conn:
            # Create users table
            self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                public_key BLOB NOT NULL,
                private_key BLOB NOT NULL
            )
            ''')

            # Create groups table
            self.conn.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                group_name TEXT PRIMARY KEY,
                public_key BLOB NOT NULL,
                private_key BLOB NOT NULL,
                leader TEXT
            )
            ''')

            # Create group_members table
            self.conn.execute('''
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
            self.conn.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                message TEXT,
                group_name TEXT,
                FOREIGN KEY (username) REFERENCES users (username)
            )
            ''')

            # Add premade accounts if the users table is empty
            self.add_premade_accounts()

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
            result = self.conn.execute('SELECT 1 FROM users WHERE username = ?', (username,)).fetchone()
            return result is not None

    def group_exists(self, group_name):
        with self.conn:
            result = self.conn.execute('SELECT 1 FROM groups WHERE group_name = ?', (group_name,)).fetchone()
            logging.debug(f"group_exists({group_name}): {result}")
            return result is not None

    def get_user_info(self, username):
        with self.conn:
            user = self.conn.execute('SELECT username, email FROM users WHERE username = ?', (username,)).fetchone()
            return user if user else None

    def get_public_key(self, username):
        with self.conn:
            public_key_serialized = self.conn.execute('''
                SELECT public_key FROM users WHERE username = ?
            ''', (username,)).fetchone()[0]
            return pickle.loads(public_key_serialized)

    def get_private_key(self, username):
        with self.conn:
            result = self.conn.execute('SELECT private_key FROM users WHERE username = ?', (username,)).fetchone()
            if result:
                return result[0]  # This ensures only the private_key column is returned
            return None
        
    def get_group_public_key(self, group_name):
        with self.conn:
            result = self.conn.execute('SELECT public_key FROM groups WHERE group_name = ?', (group_name,)).fetchone()
            if result:
                public_key_serialized = result[0]
                return pickle.loads(public_key_serialized)
            return None

    def validate_user(self, username, password):
        with self.conn:
            result = self.conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
            return result is not None

    def add_group(self, leader, group_name):
        try:
            # Generate keys for the group
            public_key, private_key = KeyGenerator.generate_keys(group_name)

            # Serialize the keys using pickle
            public_key_serialized = pickle.dumps(public_key)
            private_key_serialized = pickle.dumps(private_key)

            with self.conn:
                # Insert the group into the groups table
                self.conn.execute('''
                INSERT INTO groups (group_name, public_key, private_key, leader)
                VALUES (?, ?, ?, ?)
                ''', (group_name, public_key_serialized, private_key_serialized, leader))

                # Add the leader to the group_members table
                self.conn.execute('''
                INSERT INTO group_members (username, group_name, accepted)
                VALUES (?, ?, ?)
                ''', (leader, group_name, 1))
        except Exception as e:
            logging.error(f"Error adding group: {e}")
            raise

    def add_user_to_group(self, username, group_name):
        if not self.user_exists(username):
            raise ValueError(f"User {username} does not exist")
        if not self.group_exists(group_name):
            raise ValueError(f"Group {group_name} does not exist")

        with self.conn:
            self.conn.execute('''
            INSERT INTO group_members (username, group_name, accepted)
            VALUES (?, ?, ?)
            ''', (username, group_name, 1))

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
        if self.is_user_in_group(username, group_name):
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

    def get_group_private_key(self, group_name):
        with self.conn:
            result = self.conn.execute('SELECT private_key FROM groups WHERE group_name = ?', (group_name,)).fetchone()
            if result:
                return result[0]  # This ensures only the private_key column is returned
            return None

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
            result = self.conn.execute('SELECT * FROM notifications WHERE username = ?', (username,)).fetchall()
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