import tkinter as tk
from tkinter import messagebox
import cv2
from pyzbar.pyzbar import decode
from AESalgorithm import decrypt_aes
from RSAalgorithm import Decryption

class ScanPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.label = tk.Label(self, text="Scan QR Code")
        self.label.pack(pady=10)

        self.scan_button = tk.Button(self, text="Scan", command=self.scan_qr_code)
        self.scan_button.pack(pady=10)

        self.back_button = tk.Button(self, text="Back", command=lambda: controller.show_frame("GenerateQRPage"))
        self.back_button.pack(pady=10)

    def scan_qr_code(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            for barcode in decode(frame):
                data = barcode.data.decode('utf-8')
                private_key = self.controller.db.get_private_key(self.controller.username)
                aes_decrypted_key = Decryption(bytes.fromhex(data[:256]), private_key)  # Decrypt AES key
                decrypted_data = decrypt_aes(data[256:], aes_decrypted_key)  # Decrypt the data
                cap.release()
                cv2.destroyAllWindows()
                messagebox.showinfo("QR Code Data", decrypted_data)
                return
            cv2.imshow("Scan QR Code", frame)
            if cv2.waitKey(1) == 27:
                break
        cap.release()
        cv2.destroyAllWindows()