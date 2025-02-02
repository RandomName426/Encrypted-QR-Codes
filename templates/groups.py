import tkinter as tk
from tkinter import messagebox

class GroupsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.label = tk.Label(self, text="Groups")
        self.label.pack(pady=10)

        self.group_listbox = tk.Listbox(self)
        self.group_listbox.pack(pady=10)

        self.add_group_button = tk.Button(self, text="Add Group", command=self.add_group)
        self.add_group_button.pack(pady=10)

        self.invite_button = tk.Button(self, text="Invite to Group", command=self.invite_to_group)
        self.invite_button.pack(pady=10)

        self.kick_button = tk.Button(self, text="Kick from Group", command=self.kick_from_group)
        self.kick_button.pack(pady=10)

        self.back_button = tk.Button(self, text="Back", command=lambda: controller.show_frame("ScanPage"))
        self.back_button.pack(pady=10)

    def add_group(self):
        group_name = tk.simpledialog.askstring("Group Name", "Enter group name:")
        if group_name:
            self.controller.db.add_group(self.controller.username, group_name)
            self.update_group_list()

    def invite_to_group(self):
        selected_group = self.group_listbox.get(tk.ACTIVE)
        invitee_username = tk.simpledialog.askstring("Invite User", "Enter username to invite:")
        if selected_group and invitee_username:
            self.controller.db.invite_to_group(selected_group, invitee_username)
            messagebox.showinfo("Invite", f"User {invitee_username} invited to group {selected_group}")

    def kick_from_group(self):
        selected_group = self.group_listbox.get(tk.ACTIVE)
        kick_username = tk.simpledialog.askstring("Kick User", "Enter username to kick:")
        if selected_group and kick_username:
            self.controller.db.kick_from_group(selected_group, kick_username)
            messagebox.showinfo("Kick", f"User {kick_username} kicked from group {selected_group}")

    def update_group_list(self):
        self.group_listbox.delete(0, tk.END)
        groups = self.controller.db.get_user_groups(self.controller.username)
        for group in groups:
            self.group_listbox.insert(tk.END, group)