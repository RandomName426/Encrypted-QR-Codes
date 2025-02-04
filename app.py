from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_apscheduler import APScheduler
from utils.database import Database
from AESalgorithm import Encryption, Decryption
from utils.qr_code_maker import create_qr_code
from functools import wraps
import logging

class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key
app.config.from_object(Config())

db = Database()
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

def clean_empty_groups():
    db.delete_empty_groups()
    logging.debug("Periodic cleanup: Empty groups deleted.")

scheduler.add_job(id='CleanEmptyGroups', func=clean_empty_groups, trigger='interval', minutes=60)  # Adjust interval as needed

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

@app.route('/scan', methods=['GET', 'POST'])
@login_required
def scan():
    if request.method == 'POST':
        key_selection = request.form['key_selection']
        # Implement logic for handling key selection here
        # ...
    return render_template('scan.html', user=session['username'], groups=db.get_user_groups(session['username']))

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

@app.route('/create_group', methods=['POST'])
@login_required
def create_group():
    group_name = request.form['group_name']
    if db.group_exists(group_name):
        flash(f'Group {group_name} already exists.')
        return redirect(url_for('groups'))
    db.add_group(session['username'], group_name)
    flash(f'Group {group_name} created successfully.')
    return redirect(url_for('groups'))

def invite_to_group():
    group_name = request.form['group_name']
    username = request.form['username']

    # Check if group exists and inviter is part of the group
    if not db.group_exists(group_name):
        flash(f"Group {group_name} does not exist.")
        return redirect(url_for('groups'))

    if not db.is_user_in_group(session['username'], group_name):
        flash(f"You are not a member of the group {group_name}.")
        return redirect(url_for('groups'))

    if not db.user_exists(username):
        flash('Invalid username. Please try again.')
        return redirect(url_for('groups'))

    if db.invite_to_group(group_name, username):
        flash(f"Invitation sent to {username}.")
    else:
        flash(f"User {username} is already in the group {group_name} or has a pending invitation.")
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

if __name__ == '__main__':
    app.run(debug=True)