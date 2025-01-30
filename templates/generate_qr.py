import tkinter as tk
import qrcode
from tkinter import messagebox
from AESalgorithm import encrypt_aes
from RSAalgorithm import encrypt_rsa
from KeyGenerator import generate_keys

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

    def generate_qr_code(self):
        data = self.data_entry.get()
        aes_key = generate_keys()[0]  # Get a new public key as AES key
        nonce, ciphertext, tag = encrypt_aes(data, aes_key)
        encrypted_key = encrypt_rsa(aes_key, self.controller.username)  # Encrypt AES key with user's public key
        qr_data = f"{encrypted_key}:{nonce}:{ciphertext}:{tag}"
        qr = qrcode.QRCode()
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img.show()
        img.save("qrcode.png")
        messagebox.showinfo("QR Code", "QR Code generated and saved as qrcode.png")