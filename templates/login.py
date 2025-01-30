import tkinter as tk
from tkinter import messagebox

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.label1 = tk.Label(self, text="Username")
        self.label1.pack(pady=10)
        self.username = tk.Entry(self)
        self.username.pack(pady=10)

        self.label2 = tk.Label(self, text="Password")
        self.label2.pack(pady=10)
        self.password = tk.Entry(self, show='*')
        self.password.pack(pady=10)

        self.login_button = tk.Button(self, text="Login", command=self.login)
        self.login_button.pack(pady=10)

    def login(self):
        username = self.username.get()
        password = self.password.get()
        # Implement authentication here
        if username == "admin" and password == "password":  # Dummy check
            self.controller.show_frame("HomePage")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")