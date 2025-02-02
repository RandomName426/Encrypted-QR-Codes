from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from utils.database import Database
from AESalgorithm import encrypt_aes, decrypt_aes
from RSAalgorithm import Encryption, Decryption
from utils.qr_code_maker import create_qr_code
from secrets import randbelow
import pickle

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key
db = Database()

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db.validate_user(username, password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        recipient = request.form['recipient']
        data = request.form['data']
        public_key = db.get_public_key(recipient)
        aes_key, encrypted_message = encrypt_aes(data, randbelow(2**128 - 2**127) + 2**127)
        encrypted_key = Encryption(aes_key, public_key)
        qr_data = encrypted_key.hex() + encrypted_message
        create_qr_code(qr_data)
        flash('QR Code generated and saved as qrcode.png')
        return redirect(url_for('index'))
    return render_template('generate.html')

@app.route('/scan')
def scan():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('scan.html')

@app.route('/account')
def account():
    if 'username' not in session:
        return redirect(url_for('login'))
    user_info = db.get_user_info(session['username'])
    return render_template('account.html', user=user_info)

@app.route('/decode_qr', methods=['POST'])
def decode_qr():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    qr_data = request.json.get('qrData')
    encrypted_key_hex = qr_data[:64]
    encrypted_message = qr_data[64:]
    encrypted_key = bytes.fromhex(encrypted_key_hex)
    private_key = db.get_private_key(session['username'])
    aes_key = Decryption(encrypted_key, private_key)
    decrypted_data = decrypt_aes(encrypted_message, aes_key)
    return jsonify({'decryptedData': decrypted_data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)