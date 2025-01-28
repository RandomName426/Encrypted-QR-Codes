import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import qrcode
from io import BytesIO
import sqlite3
import json
import AESalgorithm as AES
import KeyGenerator as KG
import base64

class SecureMessagingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Messaging App")
        self.root.geometry("800x600")
        
        # Database initialization
        self.init_database()
        
        # Main container
        self.container = ttk.Frame(root)
        self.container.pack(fill="both", expand=True)
        
        # Navigation bar
        self.create_navigation()
        
        # Content frame
        self.content = ttk.Frame(self.container)
        self.content.pack(fill="both", expand=True)
        
        # Initialize frames dictionary
        self.frames = {}
        for F in (LoginPage, AccountPage, GroupsPage, ScannerPage, QRCreatorPage, NotificationsPage):
            frame = F(self.content, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame(LoginPage)

    def init_database(self):
        self.conn = sqlite3.connect('secure_messaging.db')
        c = self.conn.cursor()
        
        # Create tables
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (username TEXT PRIMARY KEY, password TEXT, email TEXT, 
                     public_key TEXT, private_key TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS groups
                    (group_id INTEGER PRIMARY KEY, name TEXT, leader TEXT,
                     public_key TEXT, private_key TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS group_members
                    (group_id INTEGER, username TEXT,
                     FOREIGN KEY(group_id) REFERENCES groups(group_id),
                     FOREIGN KEY(username) REFERENCES users(username))''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS notifications
                    (id INTEGER PRIMARY KEY, username TEXT, message TEXT, type TEXT,
                     data TEXT, read INTEGER DEFAULT 0)''')
        
        self.conn.commit()

    def create_navigation(self):
        self.nav = ttk.Frame(self.container)
        self.nav.pack(fill="x")
        
        buttons = [
            ("Account", lambda: self.show_frame(AccountPage)),
            ("Groups", lambda: self.show_frame(GroupsPage)),
            ("Scan QR", lambda: self.show_frame(ScannerPage)),
            ("Create QR", lambda: self.show_frame(QRCreatorPage)),
            ("Notifications", lambda: self.show_frame(NotificationsPage))
        ]
        
        for text, command in buttons:
            ttk.Button(self.nav, text=text, command=command).pack(side="left", padx=5, pady=5)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def register_user(self, username, password, email):
        c = self.conn.cursor()
        
        # Check if username exists
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        if c.fetchone():
            return False, "Username already exists"
            
        # Generate RSA keys
        public_key, private_key = KG.main()
        
        # Store keys as base64 strings
        public_key_str = base64.b64encode(str(public_key).encode()).decode()
        private_key_str = base64.b64encode(str(private_key).encode()).decode()
        
        # Insert user
        c.execute("""INSERT INTO users (username, password, email, public_key, private_key)
                    VALUES (?, ?, ?, ?, ?)""", 
                    (username, password, email, public_key_str, private_key_str))
        self.conn.commit()
        return True, "Registration successful"

    def login_user(self, username, password):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        if user:
            self.current_user = {
                'username': user[0],
                'email': user[2],
                'public_key': base64.b64decode(user[3].encode()).decode(),
                'private_key': base64.b64decode(user[4].encode()).decode()
            }
            return True
        return False

class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Login form
        ttk.Label(self, text="Username:").pack(pady=5)
        self.username = ttk.Entry(self)
        self.username.pack(pady=5)
        
        ttk.Label(self, text="Password:").pack(pady=5)
        self.password = ttk.Entry(self, show="*")
        self.password.pack(pady=5)
        
        ttk.Button(self, text="Login", command=self.login).pack(pady=10)
        ttk.Button(self, text="Register", command=self.show_register).pack(pady=5)
        
    def login(self):
        if self.controller.login_user(self.username.get(), self.password.get()):
            self.controller.show_frame(AccountPage)
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def show_register(self):
        # Create registration window
        register_window = tk.Toplevel(self)
        register_window.title("Register")
        register_window.geometry("300x300")
        
        ttk.Label(register_window, text="Username:").pack(pady=5)
        username = ttk.Entry(register_window)
        username.pack(pady=5)
        
        ttk.Label(register_window, text="Password:").pack(pady=5)
        password = ttk.Entry(register_window, show="*")
        password.pack(pady=5)
        
        ttk.Label(register_window, text="Email:").pack(pady=5)
        email = ttk.Entry(register_window)
        email.pack(pady=5)
        
        def register():
            success, message = self.controller.register_user(
                username.get(), password.get(), email.get())
            if success:
                messagebox.showinfo("Success", message)
                register_window.destroy()
            else:
                messagebox.showerror("Error", message)
                
        ttk.Button(register_window, text="Register", command=register).pack(pady=10)

class AccountPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        ttk.Label(self, text="Account Information").pack(pady=20)
        self.info_frame = ttk.Frame(self)
        self.info_frame.pack(pady=10)
        
    def update_info(self):
        for widget in self.info_frame.winfo_children():
            widget.destroy()
            
        user = self.controller.current_user
        if user:
            ttk.Label(self.info_frame, text=f"Username: {user['username']}").pack(pady=5)
            ttk.Label(self.info_frame, text=f"Email: {user['email']}").pack(pady=5)

class GroupsPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        ttk.Button(self, text="Create New Group", command=self.create_group).pack(pady=10)
        
        self.groups_frame = ttk.Frame(self)
        self.groups_frame.pack(fill="both", expand=True)
        
    def create_group(self):
        dialog = tk.Toplevel(self)
        dialog.title("Create New Group")
        
        ttk.Label(dialog, text="Group Name:").pack(pady=5)
        group_name = ttk.Entry(dialog)
        group_name.pack(pady=5)
        
        def save_group():
            name = group_name.get()
            if name:
                # Generate new group keys
                public_key, private_key = KG.main()
                
                c = self.controller.conn.cursor()
                c.execute("""INSERT INTO groups (name, leader, public_key, private_key)
                            VALUES (?, ?, ?, ?)""",
                         (name, self.controller.current_user['username'],
                          base64.b64encode(str(public_key).encode()).decode(),
                          base64.b64encode(str(private_key).encode()).decode()))
                
                group_id = c.lastrowid
                
                # Add creator as member
                c.execute("""INSERT INTO group_members (group_id, username)
                            VALUES (?, ?)""",
                         (group_id, self.controller.current_user['username']))
                
                self.controller.conn.commit()
                dialog.destroy()
                self.update_groups()
                
        ttk.Button(dialog, text="Create", command=save_group).pack(pady=10)
        
    def update_groups(self):
        for widget in self.groups_frame.winfo_children():
            widget.destroy()
            
        c = self.controller.conn.cursor()
        c.execute("""SELECT g.* FROM groups g
                    JOIN group_members gm ON g.group_id = gm.group_id
                    WHERE gm.username = ?""",
                 (self.controller.current_user['username'],))
                 
        for group in c.fetchall():
            frame = ttk.Frame(self.groups_frame)
            frame.pack(fill="x", pady=5)
            
            ttk.Label(frame, text=f"Group: {group[1]}").pack(side="left", padx=5)
            if group[2] == self.controller.current_user['username']:
                ttk.Button(frame, text="Invite User",
                          command=lambda g=group: self.invite_user(g[0])).pack(side="right", padx=5)

class ScannerPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.key_var = tk.StringVar()
        ttk.Label(self, text="Select decryption key:").pack(pady=5)
        self.key_combo = ttk.Combobox(self, textvariable=self.key_var)
        self.key_combo.pack(pady=5)
        
        ttk.Button(self, text="Start Scanning", command=self.start_scanning).pack(pady=10)
        
        self.result_label = ttk.Label(self, text="")
        self.result_label.pack(pady=10)
        
    def start_scanning(self):
        cap = cv2.VideoCapture(0)
        detector = cv2.QRCodeDetector()
        
        while True:
            _, img = cap.read()
            data, bbox, _ = detector.detectAndDecode(img)
            
            if data:
                try:
                    encrypted_bytes = bytes.fromhex(data)
                    key_info = eval(self.key_var.get())
                    decrypted = AES.decryption(encrypted_bytes, eval(key_info['private_key']))
                    self.result_label.config(text=f"Decrypted message: {decrypted}")
                except Exception as e:
                    self.result_label.config(text=f"Error: {str(e)}")
                break
                
            cv2.imshow("QR Scanner", img)
            if cv2.waitKey(1) == ord("q"):
                break
                
        cap.release()
        cv2.destroyAllWindows()
        
    def update_keys(self):
        c = self.controller.conn.cursor()
        
        # Get user's personal key
        personal_key = {
            'name': 'Personal Key',
            'private_key': self.controller.current_user['private_key']
        }
        
        # Get group keys
        c.execute("""SELECT g.name, g.private_key FROM groups g
                    JOIN group_members gm ON g.group_id = gm.group_id
                    WHERE gm.username = ?""",
                 (self.controller.current_user['username'],))
                 
        group_keys = [{'name': row[0], 'private_key': row[1]} for row in c.fetchall()]
        
        all_keys = [personal_key] + group_keys
        self.key_combo['values'] = [str(key) for key in all_keys]

class NotificationsPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.notifications_frame = ttk.Frame(self)
        self.notifications_frame.pack(fill="both", expand=True)
        
    def update_notifications(self):
        for widget in self.notifications_frame.winfo_children():
            widget.destroy()
            
        c = self.controller.conn.cursor()
        c.execute("""SELECT * FROM notifications
                    WHERE username = ? AND read = 0
                    ORDER BY id DESC""",
                 (self.controller.current_user['username'],))
                 
        for notif in c.fetchall():
            frame = ttk.Frame(self.notifications_frame)
            frame.pack(fill="x", pady=5)
            
            ttk.Label(frame, text=notif[2]).pack(side="left", padx=5)
            
            def mark_read(notif_id=notif[0]):
                c = self.controller.conn.cursor()
                c.execute("UPDATE notifications SET read = 1 WHERE id = ?", (notif_id,))
                self.controller.conn.commit()
                self.update_notifications()
                
            ttk.Button(frame, text="Mark as Read",
                      command=lambda: mark_read()).pack(side="right", padx=5)

def main():
    root = tk.Tk()
    app = SecureMessagingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()