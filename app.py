import tkinter as tk
from templates.scan import ScanPage
from templates.generate_qr import GenerateQRPage
from templates.account import AccountPage
from templates.groups import GroupsPage
from templates.notifications import NotificationsPage
from templates.login import LoginPage
from utils.database import Database

class QRApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Encrypted QR Code App")
        self.geometry("800x600")
        self.configure(bg="#2E4053")
        self.username = None
        self.db = Database()

        self.container = tk.Frame(self, bg="#2E4053")
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (LoginPage, ScanPage, GenerateQRPage, AccountPage, GroupsPage, NotificationsPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")
        self.navbar = None

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def create_navbar(self):
        if self.navbar:
            self.navbar.destroy()

        self.navbar = tk.Frame(self, relief="raised", bd=2, bg="#1C2833")
        self.navbar.pack(side="bottom", fill="x")

        scan_button = tk.Button(self.navbar, text="Scan", command=lambda: self.show_frame("ScanPage"), bg="#566573", fg="white")
        scan_button.pack(side="left", expand=True, fill="both")

        generate_button = tk.Button(self.navbar, text="Generate", command=lambda: self.show_frame("GenerateQRPage"), bg="#566573", fg="white")
        generate_button.pack(side="left", expand=True, fill="both")

        account_button = tk.Button(self.navbar, text="Account", command=lambda: self.show_frame("AccountPage"), bg="#566573", fg="white")
        account_button.pack(side="left", expand=True, fill="both")

        groups_button = tk.Button(self.navbar, text="Groups", command=lambda: self.show_frame("GroupsPage"), bg="#566573", fg="white")
        groups_button.pack(side="left", expand=True, fill="both")

        notifications_button = tk.Button(self.navbar, text="Notifications", command=lambda: self.show_frame("NotificationsPage"), bg="#566573", fg="white")
        notifications_button.pack(side="left", expand=True, fill="both")

if __name__ == "__main__":
    app = QRApp()
    app.mainloop()