QR Code Encryption & Decryption Web App
Overview
This web application allows users to securely encrypt data into QR codes and decrypt them using a hybrid encryption approach combining RSA and AES. It ensures secure data transmission by encrypting messages with AES and securely sharing the AES key using RSA.

Features
✅ Encrypt & Generate QR Codes – Securely encrypt text data and generate a QR code.
✅ Scan & Decrypt QR Codes – Upload or scan a QR code to decrypt the information.
✅ Hybrid Encryption (RSA + AES) – Ensures high security and efficient encryption.
✅ User Authentication – Secure login system to manage user keys.
✅ Group Encryption Support – Send encrypted messages to individual users or groups.
✅ Flash Notifications – Inform users of successful or failed actions dynamically.

How It Works
Encryption:

The user enters data and selects a recipient.
Data is encrypted using AES (Advanced Encryption Standard).
The AES key is encrypted using the recipient’s RSA public key.
The encrypted data and key are converted into a QR code.
Decryption:

The recipient scans or uploads the QR code.
The AES key is decrypted using their RSA private key.
The encrypted message is decrypted using the AES key and displayed.
Tech Stack
Frontend: HTML, CSS, JavaScript (Fetch API, JSQR for QR scanning)
Backend: Flask (Python), Jinja Templates
Encryption Libraries: PyCryptodome (for RSA/AES encryption)
Database: SQLite (or PostgreSQL/MySQL for production)
QR Code Generation: qrcode Python library
Authentication: Flask-Login
Installation & Setup
1. Clone the Repository

git clone https://github.com/yourusername/qr-encryption-app.git

cd qr-encryption-app

2. Create a Virtual Environment (Optional but Recommended)

python -m venv venv

source venv/bin/activate  # For macOS/Linux

venv\Scripts\activate      # For Windows

3. Install Dependencies

pip install -r requirements.txt

5. Run the Web App

python app.py
Then, open http://127.0.0.1:5000/ in your browser.

Usage
Sign Up & Login

Create an account and log in.
Upon registration, an RSA key pair is automatically generated for encryption.
Generate an Encrypted QR Code

Enter the recipient username and message.
The system encrypts the message and generates a QR code.
Save or download the QR code for secure transmission.
Scan or Upload to Decrypt (scanning is only usable on the host device unless the web app is adapted to use HTTPS instead of the HTTP it uses currently)

Upload an encrypted QR code or scan it using the webcam.
The system verifies the recipient’s RSA key and decrypts the message.
Security Considerations
🔒 AES for Symmetric Encryption: Fast and secure for encrypting large messages.
🔑 RSA for Key Exchange: Ensures secure sharing of AES keys.
🔍 No Plaintext Storage: Encrypted messages and keys are never stored in plaintext.
📜 Private Keys Are Local: Private keys remain on the user’s device and are never sent to the server.

Future Improvements
📲 Mobile App Integration – Extend functionality for mobile users.
🌐 End-to-End Encryption for Messages – Secure chat functionality.
🛡 Multi-Factor Authentication (MFA) – Additional layer of security.
🚀 Blockchain Integration – Secure audit logs for encrypted messages.
License
This project is licensed under the MIT License – feel free to modify and distribute it.

Contributing
Contributions are welcome! If you’d like to improve this project:

Fork the repository
Create a new branch (git checkout -b feature-branch)
Commit your changes (git commit -m "Added feature XYZ")
Push to the branch (git push origin feature-branch)
Open a Pull Request
