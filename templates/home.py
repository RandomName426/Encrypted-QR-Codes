import tkinter as tk

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.label = tk.Label(self, text="Welcome to the Home Page")
        self.label.pack(pady=10)

        self.scan_button = tk.Button(self, text="Scan QR Code", command=lambda: controller.show_frame("ScanPage"))
        self.scan_button.pack(pady=10)

        self.generate_button = tk.Button(self, text="Generate QR Code", command=lambda: controller.show_frame("GenerateQRPage"))
        self.generate_button.pack(pady=10)

        self.groups_button = tk.Button(self, text="Manage Groups", command=lambda: controller.show_frame("GroupsPage"))
        self.groups_button.pack(pady=10)

        self.notifications_button = tk.Button(self, text="Notifications", command=lambda: controller.show_frame("NotificationsPage"))
        self.notifications_button.pack(pady=10)