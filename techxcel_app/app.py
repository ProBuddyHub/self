import json
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import threading
import smtplib
import time
from email.mime.text import MIMEText
from flask_mail import Mail, Message



app = Flask(__name__)
app.secret_key = '0055'

# --- Configuration & Constants ---
TEAM_SIGNUP_CODE = "0055"          # Code required for team signup
EMAIL_TOKEN_EXPIRATION = 3600      # Token expiration: 1 hour
serializer = URLSafeTimedSerializer(app.secret_key)

# --- Email Configuration ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587            # Use 465 for SSL if needed
app.config['MAIL_USE_TLS'] = True        # Set to False if using SSL
app.config['MAIL_USE_SSL'] = False       # Set to True if using SSL
app.config['MAIL_USERNAME'] = 'panalaaditya003@gmail.com'
app.config['MAIL_PASSWORD'] = 'uahn katp kxvl nkkx'  # Use your app password if required
app.config['MAIL_DEFAULT_SENDER'] = 'panalaaditya003@gmail.com'


mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)


# File paths for storage
USERS_FILE = 'data/users.json'
EVENTS_FILE = 'data/events.json'
SETTINGS_FILE = 'data/settings.json'
POSTS_FILE = 'data/posts.json'     # For blog posts
REGISTRATIONS_FILE = "registrations.json"
TRACKING_FILE_AP = "last_update_announcements_posts.json"


# --- Helper Functions ---

def load_data(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as f:
        try:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}

def save_data(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def send_email(recipient, subject, message):
    try:
        msg = Message(subject, recipients=[recipient])
        msg.body = message
        mail.send(msg)
        print(f"✅ Email sent to {recipient}")  # Debugging statement
        return True
    except Exception as e:
        print(f"❌ Error sending email to {recipient}: {e}")  # Show error
        return False




def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        default_settings = {
            "announcements": [
                {"title": "Welcome to TechXcel", "content": "Get ready for upcoming events!"},
                {"title": "Hackathon Announcement", "content": "Join the hackathon and win exciting prizes!"}
            ],
            "star_details": {
                "name": "TechXcel Club",
                "description": "TechXcel is a club in RGUKT responsible for technical related events."
            },
            "social_links": {
                "facebook": "https://facebook.com/techxcelclub",
                "twitter": "https://twitter.com/techxcelclub",
                "instagram": "https://instagram.com/techxcelclub"
            },
            "contact_info": {
                "email": "info@techxcelclub.com",
                "phone": "+1 (555) 123-4567"
            },
            "footer_text": "© 2025 TechXcel Club. All rights reserved."
        }
        save_data(SETTINGS_FILE, default_settings)
        return default_settings
    return load_data(SETTINGS_FILE)

def send_confirmation_email(email, subject, message):
    # For demonstration, print the email details to the console.
    print(f"Sending email to {email}")
    print(f"Subject: {subject}")
    print(f"Message:\n{message}\n")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---
@app.route('/')
def index():
    if 'user_email' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

# --- Login Route ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip()
        password = request.form.get('password')
        users = load_data(USERS_FILE) or {}

        if email in users and users[email]['password'] == password:
            session['user_email'] = email
            session['user_type'] = users[email].get('user_type', 'ordinary')
            session.permanent = True  # Keep session alive for longer
            flash("Logged in successfully.", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials.", "danger")

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email').strip()
        password = request.form.get('password')
        user_type = request.form.get('user_type')

        users = load_data(USERS_FILE) or {}
        if email in users:
            flash("User already exists. Please log in.", "warning")
            return redirect(url_for('login'))

        # Store user details
        users[email] = {
            'password': password,  # Consider hashing in production
            'user_type': user_type,
            'created_at': str(datetime.now()),
            'is_verified': True  # Directly mark as verified
        }
        save_data(USERS_FILE, users)

        # Send confirmation email
        msg_body = ("Hello,\n\n"
                    "Welcome to TechXcel Event Management!\n\n"
                    "Your account has been successfully created.\n"
                    "If you face any issues, feel free to reach out to us at techxcel@rguktong.ac.in.\n\n"
                    "Best regards,\nTechXcel Team")
        
        msg = Message("Welcome to TechXcel!", recipients=[email])
        msg.body = msg_body

        try:
            mail.send(msg)
            flash("Signup successful! A confirmation email has been sent to your inbox.", "info")
        except Exception as e:
            flash("Signup successful, but there was an error sending the confirmation email: " + str(e), "warning")
        
        return redirect(url_for('login'))

    return render_template('signup.html')



def send_test_email():
    with app.app_context():
        try:
            recipient_email = "panalaaditya@gmail.com"  # Change to any email you want to test
            msg = Message('Confirmation Mail', recipients=[recipient_email])
            msg.body = 'This is a confirmation email to confirm your activities in our website. If you are not the one who initiated this, mail us at techxcel@rguktong.ac.in. Thank you.'

            mail.send(msg)
            print(f"✅ Test email sent to {recipient_email} successfully!")
        except Exception as e:
            print(f"❌ Error sending email: {e}")

@app.route('/verify/<token>')
def verify_email(token):
    try:
        email = serializer.loads(token, salt='email-confirmation-salt', max_age=3600)
    except SignatureExpired:
        flash("Verification link expired.", "danger")
        return redirect(url_for('signup'))
    except BadSignature:
        flash("Invalid verification link.", "danger")
        return redirect(url_for('signup'))

    users = load_data(USERS_FILE)
    if email in users:
        users[email]['is_verified'] = True
        save_data(USERS_FILE, users)
        flash("Email verified successfully!", "success")
    return redirect(url_for('login'))


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='email-confirmation-salt', max_age=3600)
    except SignatureExpired:
        flash("The confirmation link has expired.", "danger")
        return redirect(url_for('signup'))
    except BadSignature:
        flash("Invalid confirmation link.", "danger")
        return redirect(url_for('signup'))

    users = load_data(USERS_FILE)
    if email in users:
        users[email]['is_verified'] = True
        save_data(USERS_FILE, users)
        flash("Your email has been verified successfully. You may now log in.", "success")
    else:
        flash("User not found.", "danger")
    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    settings = load_settings()
    return render_template('home.html', settings=settings)

@app.route('/events')
@login_required
def events():
    events_data = load_data(EVENTS_FILE)
    events_list = list(events_data.values())
    return render_template('events.html', events_list=events_list)

@app.route('/blog')
def blog():
    posts = load_data(POSTS_FILE)
    posts_list = list(posts.values())
    return render_template('blog.html', posts=posts_list)

@app.route('/profile')
@login_required
def profile():
    users = load_data(USERS_FILE)
    user = users.get(session['user_email'])
    return render_template('profile.html', user=user)

@app.route('/send_custom_email', methods=['POST'])
@login_required
def send_custom_email():
    recipient = request.form.get('recipient_email')
    subject = request.form.get('email_subject')
    message = request.form.get('email_message')

    if send_email(recipient, subject, message):
        flash("Email sent successfully!", "success")
    else:
        flash("Failed to send email.", "danger")

    return redirect(url_for('home'))


@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    users = load_data(USERS_FILE)
    user_email = session.get('user_email')

    if not user_email or user_email not in users:
        return jsonify({"success": False, "message": "User not found."})

    data = request.get_json()

    # Update user details
    if "name" in data:
        users[user_email]["name"] = data["name"].strip()
    if "college_id" in data:
        users[user_email]["college_id"] = data["college_id"].strip()
    if "whatsapp" in data:
        users[user_email]["whatsapp"] = data["whatsapp"].strip()
    
    # Ensure email is not changed
    if data.get("email") != user_email:
        return jsonify({"success": False, "message": "Email cannot be changed."})

    save_data(USERS_FILE, users)

    return jsonify({"success": True, "message": "Profile updated successfully."})


# --- Control Panel Endpoints (Accessible to team members only) ---
@app.route('/edit')
@login_required
def edit():
    user_email = session.get('user_email')
    user_type = session.get('user_type')

    print(f"DEBUG: Logged-in user: {user_email}, User Type: {user_type}")

    if user_type != 'team':
        flash("Access denied. Only team members can view this page.", "danger")
        print("DEBUG: Access denied - User is NOT a team member.")
        return redirect(url_for('home'))

    print("DEBUG: Access granted - User is a team member.")

    # Load data required by the template
    events_data = load_data(EVENTS_FILE)
    settings = load_settings()
    posts_data = load_data(POSTS_FILE)

    events_list = list(events_data.values())
    posts_list = list(posts_data.values())

    return render_template('edit.html', events=events_list, settings=settings, posts=posts_list)
'''
@app.route('/register_event', methods=['POST'])
def register_event():
    data = request.get_json()
    event_id = data.get("event_id")

    if not event_id:
        return jsonify({"success": False, "error": "Invalid event ID"}), 400

    user_email = "recipient_email@gmail.com"  # Replace with dynamic email logic  

    try:
        # Create and send the email
        msg = Message("Event Registration Confirmation",
                      recipients=[user_email])
        msg.body = f"Hello,\n\nYou have successfully registered for the event!\n\nEvent ID: {event_id}\n\nThank you!"
        mail.send(msg)

        return jsonify({"success": True, "message": "Registered successfully. Email sent!"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
'''
"""his one is working well. Use this in case. 

from flask import session

@app.route('/register_event', methods=['POST'])
def register_event():
    try:
        data = request.get_json()
        print("Received Data:", data)  # Debugging

        if not data:
            return jsonify({"success": False, "error": "No JSON data received"}), 400

        event_id = data.get("event_id")
        event_name = data.get("event_name")
        print(event_name)

        # Get email from session (if user is logged in)
        user_email = session.get("user_email")  

        if not event_id or not user_email:
            return jsonify({"success": False, "error": "Invalid event ID or user not logged in"}), 400

        # Send confirmation email
        msg = Message("Event Registration Confirmation",
                      recipients=[user_email])
        msg.body = f"Hello,\n\nYou have successfully registered for the event: {event_name}!\n\nEvent ID: {event_id}\n\nThank you!"
        mail.send(msg)

        return jsonify({"success": True, "message": "Registered successfully. Email sent!"}), 200

    except Exception as e:
        print(f"❌ Error: {e}")  # Debugging
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/register_event', methods=['POST'])
def register_event():
    try:
        data = request.get_json()
        print("Received Data:", data)  # Debugging

        if not data:
            return jsonify({"success": False, "error": "No JSON data received"}), 400

        event_id = data.get("event_id")
        user_email = session.get("user_email")

        if not event_id or not user_email:
            return jsonify({"success": False, "error": "Invalid event ID or user not logged in"}), 400

        # Load event details
        if os.path.exists(EVENTS_FILE):
            with open(EVENTS_FILE, "r") as file:
                try:
                    events = json.load(file)
                except json.JSONDecodeError:
                    events = {}
        else:
            events = {}

        # Check if event exists
        if event_id not in events:
            return jsonify({"success": False, "error": "Event not found!"}), 404

        event_name = events[event_id]["name"]  # Fetch event name

        # Load existing registrations
        if os.path.exists(REGISTRATIONS_FILE):
            with open(REGISTRATIONS_FILE, "r") as file:
                try:
                    registrations = json.load(file)
                except json.JSONDecodeError:
                    registrations = []
        else:
            registrations = []

        # Prevent duplicate registrations
        for reg in registrations:
            if reg["event_id"] == event_id and reg["user_email"] == user_email:
                return jsonify({"success": False, "message": "User already registered!"}), 200

        # Register user
        registrations.append({
            "event_id": event_id,
            "event_name": event_name,  # Store actual event name
            "user_email": user_email
        })

        # Save to file
        with open(REGISTRATIONS_FILE, "w") as file:
            json.dump(registrations, file, indent=4)

        # Send confirmation email
        msg = Message("Event Registration Confirmation",
                      recipients=[user_email])
        msg.body = f"Hello,\n\nYou have successfully registered for the event: {event_name}!\n\nEvent ID: {event_id}\n\nThank you!"
        mail.send(msg)

        return jsonify({"success": True, "message": "Registered successfully. Email sent!"}), 200

    except Exception as e:
        print(f"❌ Error: {e}")  # Debugging
        return jsonify({"success": False, "error": str(e)}), 500
"""

# Load JSON data
def load_json(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save JSON data
def save_json(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

@app.route('/register_event', methods=['POST'])
def register_event():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No JSON data received"}), 400

        event_id = data.get("event_id")
        user_email = session.get("user_email")  
        
        if not event_id or not user_email:
            return jsonify({"success": False, "error": "Invalid event ID or user not logged in"}), 400

        events = load_json(EVENTS_FILE)
        registrations = load_json(REGISTRATIONS_FILE)

        event = events.get(event_id)
        if not event:
            return jsonify({"success": False, "error": "Event not found"}), 404

        event_date = datetime.strptime(event["date"], "%Y-%m-%d")
        today = datetime.today().date()

        # Store registration details
        registrations.append({"event_id": event_id, "user_email": user_email})
        save_json(REGISTRATIONS_FILE, registrations)

        # Send immediate reminder
        if event_date.date() > today:
            send_email(user_email, "Event Reminder", f"Reminder: Your event {event['name']} is on {event['date']}.")
        send_email(user_email, "Event Day Reminder", f"Today is your event {event['name']}! Don't forget to attend.")

        return jsonify({"success": True, "message": "Registered successfully. Email sent!"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def send_email(to_email, subject, body):
    try:
        msg = Message(subject, recipients=[to_email])
        msg.body = body
        mail.send(msg)
        print(f"✅ Email sent to {to_email}: {subject}")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")


@app.route('/create_event', methods=['POST'])
@login_required
def create_event():
    event_data = {
        "id": f"event{int(datetime.now().timestamp())}",  # ✅ Correct
        "name": request.form.get('event_name'),
        "date": request.form.get('event_date'),
        "location": request.form.get('event_location'),
        "description": request.form.get('event_description')
    }

    events = load_data(EVENTS_FILE)
    events[event_data["id"]] = event_data
    save_data(EVENTS_FILE, events)

    # Notify all users via email
    users = load_data(USERS_FILE)
    subject = f"New Event: {event_data['name']}"
    message = f"An event '{event_data['name']}' is scheduled on {event_data['date']} at {event_data['location']}.\nDetails: {event_data['description']}"

    for email in users:
        send_email(email, subject, message)

    flash("Event created and notifications sent!", "success")
    return redirect(url_for('home'))


@app.route('/delete_event/<event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    events = load_data(EVENTS_FILE)
    if event_id in events:
        del events[event_id]
        save_data(EVENTS_FILE, events)
        flash("Event deleted successfully.", "success")
    else:
        flash("Event not found.", "danger")
    return redirect(url_for('edit'))

@app.route('/create_announcement', methods=['POST'])
@login_required
def create_announcement():
    title = request.form.get('announcement_title')
    content = request.form.get('announcement_content')
    settings = load_settings()
    new_ann = {"title": title, "content": content}
    settings.setdefault("announcements", []).append(new_ann)
    save_data(SETTINGS_FILE, settings)
    
    # **Trigger Email Notification with the New Announcement**
    notify_new_announcements_posts(new_ann=new_ann)
    
    flash("Announcement created successfully.", "success")
    return redirect(url_for('edit'))




@app.route('/create_post', methods=['POST'])
@login_required
def create_post():
    title = request.form.get('post_title')
    content = request.form.get('post_content')
    
    # Use the correct datetime reference (since we imported datetime from datetime)
    post_id = "post" + str(int(datetime.now().timestamp()))
    
    posts = load_data(POSTS_FILE)
    posts[post_id] = {"id": post_id, "title": title, "content": content}
    save_data(POSTS_FILE, posts)
    
    # Prepare email notification details
    subject = "New Post Alert"
    body = f"A new post titled '{title}' has been added. Visit the website to read it."
    
    # Load all user emails from USERS_FILE and send notification
    users = load_data(USERS_FILE)
    for user_email in users.keys():
        send_email(user_email, subject, body)
    
    flash("Post created successfully. Email notifications sent.", "success")
    return redirect(url_for('edit'))



@app.route('/delete_announcement', methods=['POST'])
@login_required
def delete_announcement():
    title = request.form.get('announcement_title')
    settings = load_settings()
    announcements = settings.get("announcements", [])
    new_announcements = [ann for ann in announcements if ann["title"] != title]
    
    if len(new_announcements) < len(announcements):  # Means deletion happened
        settings["announcements"] = new_announcements
        save_data(SETTINGS_FILE, settings)
        
        # **Trigger Email Notification**
        notify_new_announcements_posts()
        
        flash("Announcement deleted successfully.", "success")
    else:
        flash("Announcement not found.", "danger")
    
    return redirect(url_for('edit'))

@app.route('/delete_post/<post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    posts = load_data(POSTS_FILE)
    
    if post_id in posts:
        del posts[post_id]
        save_data(POSTS_FILE, posts)
        
        # **Trigger Email Notification**
        notify_new_announcements_posts()
        
        flash("Post deleted successfully.", "success")
    else:
        flash("Post not found.", "danger")
    
    return redirect(url_for('edit'))

# Helper function: do not change its name.
def send_email(recipient, subject, message):
    try:
        with app.app_context():  # Ensure the email is sent within the Flask app context
            msg = Message(subject, recipients=[recipient])
            msg.body = message
            mail.send(msg)
            print(f"✅ Email sent to {recipient}")
        return True
    except Exception as e:
        print(f"❌ Error sending email to {recipient}: {e}")
        return False



# Route for sending a confirmation email via a form submission
@app.route('/send_email_api', methods=['POST'])
def send_email_api():
    try:
        data = request.get_json()
        print("Received Data:", data)  # Debugging

        if not data:
            return jsonify({"status": "error", "message": "No JSON data received"}), 400

        event_id = data.get("event_id")
        user_email = data.get("user_email")


        if not user_email or not event_id:
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        subject = "Event Registration Confirmation"
        body = f"Hello,\n\nYou have successfully registered for the event!\n\nEvent ID: {event_id}\n\nThank you!"

        # Sending email using Flask-Mail
        msg = Message(subject, recipients=[user_email])
        msg.body = body
        mail.send(msg)

        return jsonify({"status": "success", "message": f"Email sent to {user_email}"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
# Background function to monitor events.json
def monitor_events():
    previous_events = load_json(EVENTS_FILE)

    while True:
        time.sleep(1)  # Check every second
        current_events = load_json(EVENTS_FILE)

        prev_event_ids = set(previous_events.keys())
        curr_event_ids = set(current_events.keys())

        # Detect new events
        new_events = curr_event_ids - prev_event_ids
        for event_id in new_events:
            event = current_events[event_id]
            subject = f"🚀 New Event Added: {event['name']}!"
            body = f"A new event has been added!\n\nEvent: {event['name']}\nDate: {event['date']}\nLocation: {event['location']}\n\nCheck the website for more details!"
            notify_users(subject, body)

        # Detect deleted events
        deleted_events = prev_event_ids - curr_event_ids
        for event_id in deleted_events:
            event = previous_events[event_id]
            subject = f"❌ Event Canceled: {event['name']}"
            body = f"The event '{event['name']}' scheduled on {event['date']} at {event['location']} has been canceled.\n\nWe regret any inconvenience caused."
            notify_users(subject, body)

        # Update previous state
        previous_events = current_events.copy()

# Function to notify all users
def notify_users(subject, body):
    users = load_json(USERS_FILE)
    for user_email in users.keys():
        send_email(user_email, subject, body)

# Start the monitoring thread
event_monitor_thread = threading.Thread(target=monitor_events, daemon=True)
event_monitor_thread.start()

print("✅ Event monitoring started! Listening for changes in events.json...")
'''
def notify_new_announcements_posts():
    print("🚀 notify_new_announcements_posts() triggered")
    
    settings = load_settings()
    announcements = settings.get("announcements", [])
    posts = load_data(POSTS_FILE)
    
    if not announcements and not posts:
        print("🔎 No announcements or posts found.")
        return
    
    print(f"📢 Announcements count: {len(announcements)}")
    print(f"📝 Posts count: {len(posts)}")

    subject = "New Announcement/Post Update"
    body = f"Latest Announcements: {len(announcements)}\nLatest Posts: {len(posts)}"
    users = load_data(USERS_FILE)

    for email in users:
        send_email(email, subject, body)
    
    print("📩 Email notifications sent!")
'''

def notify_new_announcements_posts(new_ann=None, new_post_title=None):
    print("🚀 notify_new_announcements_posts() triggered")

    subject = ""
    body = ""

    if new_ann:  # If a new announcement was added
        subject = f"📢 New Announcement: {new_ann['title']}"
        body = f"**{new_ann['title']}**\n\n{new_ann['content']}\n\nCheck the platform for more details!"
    
    elif new_post_title:  # If a new post was added
        subject = "📝 A New Post Has Been Added!"
        body = f"A new post titled **'{new_post_title}'** has been added.\nVisit the platform to check it out!"

    users = load_json(USERS_FILE)
    if subject and body:
        for email in users:
            send_email(email, subject, body)
        print(f"📩 Email notifications sent! Subject: {subject}")
    else:
        print("🔎 No new announcement or post to notify.")


@app.route('/test-email')
def test_email():
    notify_new_announcements_posts()
    return "Email test completed!"






if __name__ == '__main__':
    # Ensure data folder and users file exist
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists(USERS_FILE):
        save_data(USERS_FILE, {})
    send_test_email()
    if not os.path.exists('data'):
        os.makedirs('data')
    for file in [USERS_FILE, EVENTS_FILE, SETTINGS_FILE, POSTS_FILE]:
        if not os.path.exists(file):
            if file == SETTINGS_FILE:
                default_settings = {
                    "announcements": [
                        {"title": "Welcome to TechXcel", "content": "Get ready for upcoming events!"},
                        {"title": "Hackathon Announcement", "content": "Join the hackathon and win exciting prizes!"}
                    ],
                    "star_details": {
                        "name": "TechXcel Club",
                        "description": "TechXcel is a club in RGUKT responsible for technical related events."
                    },
                    "social_links": {
                        "facebook": "https://facebook.com/techxcelclub",
                        "twitter": "https://twitter.com/techxcelclub",
                        "instagram": "https://instagram.com/techxcelclub"
                    },
                    "contact_info": {
                        "email": "info@techxcelclub.com",
                        "phone": "9133770055"
                    },
                    "footer_text": "© 2025 TechXcel Club. All rights reserved."
                }
                with open(file, 'w') as f:
                    json.dump(default_settings, f, indent=4)
            else:
                with open(file, 'w') as f:
                    json.dump({}, f)
    app.run(debug=True)
