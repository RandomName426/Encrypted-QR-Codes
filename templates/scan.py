import tkinter as tk
from tkinter import messagebox
import cv2
from pyzbar.pyzbar import decode
from AESalgorithm import decrypt_aes
from RSAalgorithm import decrypt_rsa
from KeyGenerator import get_private_key

class ScanPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.label = tk.Label(self, text="Scan QR Code")
        self.label.pack(pady=10)

        self.scan_button = tk.Button(self, text="Scan", command=self.scan_qr_code)
        self.scan_button.pack(pady=10)

    def scan_qr_code(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            for barcode in decode(frame):
                data = barcode.data.decode('utf-8')
                # Decrypt the data here
                aes_key_encrypted, encrypted_data = self.split_data(data)
                private_key = get_private_key(self.controller.username)  # Get user's private key
                aes_key = decrypt_rsa(aes_key_encrypted, private_key)
                decrypted_data = decrypt_aes(*encrypted_data, aes_key)  # Pass nonce, ciphertext, tag
                cap.release()
                cv2.destroyAllWindows()
                messagebox.showinfo("QR Code Data", decrypted_data)
                return
            cv2.imshow("Scan QR Code", frame)
            if cv2.waitKey(1) == 27:
                break
        cap.release()
        cv2.destroyAllWindows()

    def split_data(self, data):
        # Implement logic to split the data into AES key and encrypted data
        aes_key_encrypted, nonce, ciphertext, tag = data.split(':')
        return aes_key_encrypted, (nonce, ciphertext, tag)