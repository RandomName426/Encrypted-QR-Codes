import sqlite3

def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for column in columns:
        if column[1] == column_name:
            return True
    return False

def migrate_db(db_path='app.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if the 'accepted' column exists before adding it
    if not column_exists(cursor, 'group_members', 'accepted'):
        cursor.execute('''
            ALTER TABLE group_members ADD COLUMN accepted INTEGER DEFAULT 0
        ''')
        print("Column 'accepted' added to 'group_members' table.")
    else:
        print("Column 'accepted' already exists in 'group_members' table.")

    conn.commit()
    conn.close()

migrate_db()