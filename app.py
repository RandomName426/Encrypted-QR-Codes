from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from utils.database import Database
from AESalgorithm import Encryption, Decryption
from utils.qr_code_maker import create_qr_code
from functools import wraps
import zlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key
db = Database()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db.validate_user(username, password):
            session['username'] = username  # Store the username in the session
            flash('Logged in successfully.')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    if request.method == 'POST':
        recipient = request.form['recipient']
        data = request.form['data']
        if not db.user_exists(recipient):
            flash('Invalid username. Please try again.')
            return redirect(url_for('generate'))
        public_key = db.get_public_key(recipient)
        print(f"Public Key: {public_key}")
        encrypted_data = Encryption(data, public_key)
        qr_data = encrypted_data.hex()
        create_qr_code(qr_data)
        flash('QR Code generated and saved as qrcode.png')
        return redirect(url_for('index'))
    return render_template('generate.html')

@app.route('/scan')
@login_required
def scan():
    return render_template('scan.html')

@app.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    if request.method == 'POST':
        group_name = request.form['group_name']
        db.add_group(session['username'], group_name)
        flash(f'Group {group_name} created successfully.')
        return redirect(url_for('account'))
    return render_template('create_group.html')

@app.route('/invite_to_group', methods=['POST'])
@login_required
def invite_to_group():
    group_name = request.form['group_name']
    username = request.form['username']
    db.invite_to_group(group_name, username)
    flash(f'Invitation sent to {username}.')
    return redirect(url_for('account'))

@app.route('/notifications')
@login_required
def notifications():
    notifications = db.get_notifications(session['username'])
    return render_template('notifications.html', notifications=notifications)

@app.route('/account')
@login_required
def account():
    username = session.get('username')
    if username:
        user_info = db.get_user_info(username)
        groups = db.get_user_groups(username)
        if user_info:
            user = {'username': user_info[0], 'email': user_info[1], 'groups': groups}
            return render_template('account.html', user=user)
    return "User not found", 404

@app.route('/decode_qr', methods=['POST'])
@login_required
def decode_qr():
    try:
        # Read the QR data from the request
        qr_data = request.data

        if not qr_data:
            return jsonify({'error': 'No QR data provided'}), 400

        # Decompress the QR data
        decompressed_data = zlib.decompress(qr_data)

        # Retrieve the username from the session
        username = session.get('username')
        if not username:
            return jsonify({'error': 'User not logged in'}), 401

        # Get the private key for decryption
        private_key = db.get_private_key(username)  # Replace with your method to get the private key
        print(f"Private Key: {private_key}")
        # Decrypt the decompressed data
        decrypted_data = Decryption(decompressed_data, private_key)

        return jsonify({'decryptedData': decrypted_data})
    except Exception as e:
        print(f"Error decoding QR code: {e}")
        return jsonify({'error': 'Failed to decode QR code'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)