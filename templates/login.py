import tkinter as tk
from tkinter import messagebox

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg="#2E4053")

        self.label = tk.Label(self, text="Login", font=("Helvetica", 18, "bold"), bg="#2E4053", fg="white")
        self.label.pack(pady=20)

        self.username_label = tk.Label(self, text="Username", bg="#2E4053", fg="white")
        self.username_label.pack(pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)

        self.password_label = tk.Label(self, text="Password", bg="#2E4053", fg="white")
        self.password_label.pack(pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        self.login_button = tk.Button(self, text="Login", command=self.login, bg="#566573", fg="white")
        self.login_button.pack(pady=20)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.controller.db.validate_user(username, password):
            self.controller.username = username
            self.controller.show_frame("ScanPage")
            self.controller.create_navbar()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")