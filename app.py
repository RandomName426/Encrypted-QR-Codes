import tkinter as tk
from templates.scan import ScanPage
from templates.generate_qr import GenerateQRPage
from templates.account import AccountPage
from templates.groups import GroupsPage
from templates.notifications import NotificationsPage
from utils.database import Database

class QRApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Encrypted QR Code App")
        self.geometry("800x600")
        self.username = None
        self.db = Database()

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (ScanPage, GenerateQRPage, AccountPage, GroupsPage, NotificationsPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("AccountPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

if __name__ == "__main__":
    app = QRApp()
    app.mainloop()