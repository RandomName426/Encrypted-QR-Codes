import tkinter as tk
from tkinter import messagebox
from AESalgorithm import encrypt_aes
from RSAalgorithm import Encryption
from utils.qr_code_maker import create_qr_code
from secrets import randbelow

class GenerateQRPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.label = tk.Label(self, text="Enter Data to Encode")
        self.label.pack(pady=10)

        self.data_entry = tk.Entry(self)
        self.data_entry.pack(pady=10)

        self.generate_button = tk.Button(self, text="Generate QR Code", command=self.generate_qr_code)
        self.generate_button.pack(pady=10)

        self.back_button = tk.Button(self, text="Back", command=lambda: controller.show_frame("ScanPage"))
        self.back_button.pack(pady=10)

    def generate_qr_code(self):
        data = self.data_entry.get()
        recipient_username = self.controller.username  # Replace with actual recipient username
        public_key = self.controller.db.get_public_key(recipient_username)
        aes_key, encrypted_message = encrypt_aes(data, randbelow(2**128 - 2**127) + 2**127)
        encrypted_key = Encryption(aes_key, public_key)
        qr_data = encrypted_key.hex() + encrypted_message
        create_qr_code(qr_data)
        messagebox.showinfo("QR Code", "QR Code generated and saved as qrcode.png")