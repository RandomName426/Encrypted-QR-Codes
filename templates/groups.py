import tkinter as tk
from tkinter import messagebox

class GroupsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.label = tk.Label(self, text="Groups")
        self.label.pack(pady=10)

        self.new_group_button = tk.Button(self, text="Create New Group", command=self.create_group)
        self.new_group_button.pack(pady=10)

        self.groups_listbox = tk.Listbox(self)
        self.groups_listbox.pack(pady=10)

        self.load_groups()

    def create_group(self):
        # Implement group creation logic
        pass

    def load_groups(self):
        # Implement logic to load groups
        pass