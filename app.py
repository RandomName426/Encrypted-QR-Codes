import tkinter as tk
from templates.login import LoginPage
from templates.home import HomePage
from templates.scan import ScanPage
from templates.generate_qr import GenerateQRPage
from templates.groups import GroupsPage
from templates.notifications import NotificationsPage

class MainApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Encrypted QR Codes App")

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginPage, HomePage, ScanPage, GenerateQRPage, GroupsPage, NotificationsPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()