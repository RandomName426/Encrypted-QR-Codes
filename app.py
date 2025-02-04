from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from utils.database import Database
from AESalgorithm import Encryption, Decryption
from utils.qr_code_maker import create_qr_code
from functools import wraps
import zlib
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key
db = Database()
logging.basicConfig(level=logging.DEBUG)

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
        
        # Check if the recipient is a user or a group
        if db.user_exists(recipient):
            public_key = db.get_public_key(recipient)
        elif db.group_exists(recipient):
            public_key = db.get_group_public_key(recipient)
        else:
            flash('Invalid recipient. Please enter a valid username or group name.')
            return redirect(url_for('generate'))

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
    username = session['username']
    user_info = db.get_user_info(username)
    user_private_keys = [db.get_private_key(username)]  # Fetch the user's private key
    user_groups = db.get_user_groups(username)
    group_private_keys = {group: db.get_group_private_key(group) for group in user_groups}
    return render_template('scan.html', user=user_info, user_keys=user_private_keys, group_keys=group_private_keys)

@app.route('/account', methods=['GET'])
@login_required
def account():
    try:
        username = session.get('username')
        if not username:
            flash('User not logged in', 'danger')
            return redirect(url_for('login'))

        user_info = db.get_user_info(username)
        if not user_info:
            flash('User not found', 'danger')
            return redirect(url_for('login'))

        groups = db.get_user_groups(username)
        if groups is None:
            groups = []

        user = {'username': user_info[0], 'email': user_info[1], 'groups': groups}

        return render_template('account.html', user=user)
    except Exception as e:
        logging.error(f"Error loading account page: {e}")
        flash('An error occurred while loading your account information', 'danger')
        return redirect(url_for('index'))

@app.route('/create_group', methods=['POST'])
@login_required
def create_group():
    group_name = request.form['group_name']
    db.add_group(session['username'], group_name)
    flash('Group created successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/add_user_to_group', methods=['POST'])
@login_required
def add_user_to_group():
    username = request.form['username']
    group_name = request.form['group_name']
    try:
        db.add_user_to_group(username, group_name)
        flash('User added to group successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('index'))

@app.route('/invite_to_group', methods=['POST'])
@login_required
def invite_to_group():
    group_name = request.form['group_name']
    username = request.form['username']

    logging.debug(f"Inviting {username} to group {group_name} by {session['username']}")

    # Check if group exists and inviter is part of the group
    if not db.group_exists(group_name):
        flash(f"Group {group_name} does not exist.")
        logging.error(f"Group {group_name} does not exist.")
        return redirect(url_for('groups'))

    if not db.is_user_in_group(session['username'], group_name):
        flash(f"You are not a member of the group {group_name}.")
        logging.error(f"User {session['username']} is not a member of group {group_name}.")
        return redirect(url_for('groups'))

    if not db.user_exists(username):
        flash('Invalid username. Please try again.')
        logging.error(f"User {username} does not exist.")
        return redirect(url_for('groups'))

    if db.invite_to_group(group_name, username):
        flash(f"Invitation sent to {username}.")
        logging.info(f"Invitation sent to {username} for group {group_name}.")
    else:
        flash(f"User {username} is already in the group {group_name} or has a pending invitation.")
        logging.error(f"User {username} is already in the group {group_name} or has a pending invitation.")
    return redirect(url_for('groups'))

@app.route('/leave_group', methods=['POST'])
@login_required
def leave_group():
    group_name = request.form['group_name']
    db.leave_group(group_name, session['username'])
    db.delete_empty_groups()  # Clean up empty groups
    flash(f'You have left the group {group_name}.')
    return redirect(url_for('account'))

@app.route('/groups')
@login_required
def groups():
    user_groups = db.get_user_groups(session['username'])
    all_groups = db.get_all_groups()
    return render_template('groups.html', user_groups=user_groups, all_groups=all_groups)

@app.route('/notifications')
@login_required
def notifications():
    notifications = db.get_user_notifications(session['username'])
    return render_template('notifications.html', notifications=notifications)

@app.route('/notifications/<int:notification_id>')
@login_required
def view_notification(notification_id):
    notification = db.get_notification_by_id(notification_id)
    if notification['username'] == session['username']:
        db.delete_notification(notification_id)
        return render_template('notifications.html', selected_notification=notification, notifications=db.get_user_notifications(session['username']))
    return redirect(url_for('notifications'))

@app.route('/accept_invitation/<int:notification_id>', methods=['POST'])
@login_required
def accept_invitation(notification_id):
    logging.debug(f"Received accept invitation request for notification ID: {notification_id}")

    notification = db.get_notification_by_id(notification_id)
    if notification is None:
        logging.error(f"Notification not found for ID: {notification_id}")
        return jsonify({"error": "Notification not found"}), 404

    group_name = notification['group_name']
    username = notification['username']

    db.accept_invitation(group_name, username)
    db.delete_notification(notification_id)
    flash(f'Invitation to join {group_name} accepted.')
    return redirect(url_for('notifications'))

@app.route('/decline_invitation/<int:notification_id>', methods=['POST'])
@login_required
def decline_invitation(notification_id):
    logging.debug(f"Received decline invitation request for notification ID: {notification_id}")

    notification = db.get_notification_by_id(notification_id)
    if notification is None:
        logging.error(f"Notification not found for ID: {notification_id}")
        return jsonify({"error": "Notification not found"}), 404

    group_name = notification['group_name']
    username = notification['username']

    db.decline_invitation(group_name, username)
    db.delete_notification(notification_id)
    flash(f'Invitation to join {group_name} declined.')
    return redirect(url_for('notifications'))

@app.route('/decode_qr', methods=['POST'])
@login_required
def decode_qr():
    try:
        data = request.get_json()
        qr_data = bytes(data['qrData'])
        key_selection = data['key_selection']
        # Debugging information
        logging.debug(f"QR Data: {qr_data}")
        logging.debug(f"Key Selection: {key_selection}")

        if not qr_data:
            return jsonify({'error': 'No QR data provided'}), 400

        # Decompress the QR data
        try:
            decompressed_data = zlib.decompress(qr_data)
        except zlib.error as e:
            logging.error(f"Decompression error: {e}")
            return jsonify({'error': 'Decompression error'}), 400
        print(decompressed_data)
        # Determine if the key selection is a user or a group
        if key_selection == session['username']:
            private_key = db.get_private_key(session['username'])
        elif db.group_exists(key_selection):
            private_key = db.get_group_private_key(key_selection)
        else:
            return jsonify({'error': 'Invalid key selection'}), 400

        # Debugging information
        logging.debug(f"Private Key: {private_key}")

        # Decrypt the decompressed data
        try:
            decrypted_data = Decryption(decompressed_data, private_key)
        except Exception as e:
            logging.error(f"Decryption error: {e}")
            return jsonify({'error': 'Decryption error'}), 400

        return jsonify({'decryptedData': decrypted_data})
    except Exception as e:
        logging.error(f"Error decoding QR code: {e}")
        return jsonify({'error': str(e)}), 500
    
# @app.route('/decode_qr', methods=['POST'])
# @login_required
# def decode_qr_endpoint():
#     key_selection = request.form['key_selection']
#     qr_code_file = request.files['qr_code']
#     qr_code_content = qr_code_file.read()
    
#     try:
#         # Decompress the QR data
#         try:
#             decompressed_data = zlib.decompress(qr_code_content)
#         except zlib.error as e:
#             logging.error(f"Decompression error: {e}")
#             return jsonify({'error': 'Decompression error'}), 400

#         # Determine if the key selection is a user or a group
#         if key_selection == session['username']:
#             private_key = db.get_private_key(session['username'])
#         elif db.group_exists(key_selection):
#             private_key = db.get_group_private_key(key_selection)
#         else:
#             return jsonify({'error': 'Invalid key selection'}), 400

#         # Debugging information
#         logging.debug(f"Private Key: {private_key}")

#         # Decrypt the decompressed data
#         try:
#             decrypted_data = Decryption(decompressed_data, private_key)
#         except Exception as e:
#             logging.error(f"Decryption error: {e}")
#             return jsonify({'error': 'Decryption error'}), 400

#         return jsonify({'decryptedData': decrypted_data})
#     except Exception as e:
#         logging.error(f"Error decoding QR code: {e}")
#         return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)