import tkinter as tk

class NotificationsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.label = tk.Label(self, text="Notifications")
        self.label.pack(pady=10)

        self.notifications_listbox = tk.Listbox(self)
        self.notifications_listbox.pack(pady=10)

        self.back_button = tk.Button(self, text="Back", command=lambda: controller.show_frame("ScanPage"))
        self.back_button.pack(pady=10)

    def update_notifications(self):
        self.notifications_listbox.delete(0, tk.END)
        notifications = self.controller.db.get_notifications(self.controller.username)
        for notification in notifications:
            self.notifications_listbox.insert(tk.END, notification)