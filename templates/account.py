import tkinter as tk

class AccountPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.label = tk.Label(self, text="Account Information")
        self.label.pack(pady=10)

        self.info_label = tk.Label(self, text="")
        self.info_label.pack(pady=10)

        self.back_button = tk.Button(self, text="Back", command=lambda: controller.show_frame("ScanPage"))
        self.back_button.pack(pady=10)

    def show_account_info(self):
        user_info = self.controller.db.get_user_info(self.controller.username)
        info_text = f"Username: {user_info['username']}\nEmail: {user_info['email']}"
        self.info_label.config(text=info_text)