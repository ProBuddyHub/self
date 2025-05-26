'''

import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email credentials (Replace with your details)
SMTP_SERVER = "smtp.gmail.com"  # Gmail SMTP server
SMTP_PORT = 587
EMAIL_SENDER = "panalaaditya003@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "uahn katp kxvl nkkx"  # Use App Password for Gmail
EMAIL_RECEIVER = "panalaaditya@gmail.com"  # Replace with recipient email

def send_test_email():
    try:
        # Create email message
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = "Automated Test Email"

        body = "This is an automated email sent every 5 seconds."
        msg.attach(MIMEText(body, "plain"))

        # Connect to SMTP server and send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure connection
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()

        print("Email sent successfully!")

    except Exception as e:
        print("Error sending email:", str(e))

# Run every 5 seconds
while True:
    send_test_email()
    time.sleep(5)  # Wait 5 seconds before sending the next email

'''


'''
import json
import smtplib
import time
from datetime import datetime
from email.mime.text import MIMEText

# --- Email Configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "panalaaditya003@gmail.com"
SENDER_PASSWORD = "uahn katp kxvl nkkx"  # Make sure this is an app password!

# --- File Paths ---
EVENTS_FILE = "/home/user/data/events.json"
REGISTRATIONS_FILE = "/home/user/Documents/Tech_Xcel/techxcel_app/templates/registrations.json"

def send_email(recipient, subject, body):
    """Function to send an email"""
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient, msg.as_string())

        print(f"✅ Email sent to {recipient}")

    except Exception as e:
        print(f"❌ Failed to send email to {recipient}: {e}")

def send_event_reminders():
    """Send reminders to users whose registered event is today"""
    try:
        # Load event data
        with open(EVENTS_FILE, "r") as file:
            events = json.load(file)

        # Load registration data
        with open(REGISTRATIONS_FILE, "r") as file:
            registrations = json.load(file)

        # Get today's date
        today = datetime.today().strftime("%Y-%m-%d")

        for reg in registrations:
            event_id = reg["event_id"]
            user_email = reg["user_email"]

            # Check if the event exists and is scheduled for today
            event = events.get(event_id)
            if event and event["date"] == today:
                subject = f"Reminder: {event['name']} is Today!"
                body = (
                    f"Hello,\n\nYour registered event '{event['name']}' is happening today at {event['location']}.\n\n"
                    "Don't miss it!\n\nBest regards,\nEvent Team"
                )
                send_email(user_email, subject, body)

    except Exception as e:
        print(f"❌ Error processing reminders: {e}")

if __name__ == "__main__":
    while True:
        send_event_reminders()
        print("⏳ Waiting 5 seconds before checking again...")
        time.sleep(50)  # Run every 5 seconds (for testing)
'''

'''
import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

EVENTS_FILE = "/home/user/data/events.json"
REGISTRATIONS_FILE = "/home/user/Documents/Tech_Xcel/techxcel_app/templates/registrations.json"

# Email Config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "panalaaditya003@gmail.com"
SMTP_PASSWORD = "uahn katp kxvl nkkx"

def load_json(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def send_email(to_email, subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_USERNAME
        msg["To"] = to_email

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to_email, msg.as_string())

        print(f"✅ Email sent to {to_email}: {subject}")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")

def send_event_day_reminders():
    events = load_json(EVENTS_FILE)
    registrations = load_json(REGISTRATIONS_FILE)

    today = datetime.today().date().strftime("%Y-%m-%d")

    for reg in registrations:
        event_id = reg["event_id"]
        user_email = reg["user_email"]
        
        event = events.get(event_id)
        if event and event["date"] == today:
            send_email(user_email, "Event Day Reminder", f"Today is your event {event['name']}! Don't forget to attend.")

if __name__ == "__main__":
    send_event_day_reminders()
'''


import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# File Paths
EVENTS_FILE = "/home/user/data/events.json"
REGISTRATIONS_FILE = "/home/user/Documents/Tech_Xcel/techxcel_app/templates/registrations.json"

# Email Config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "panalaaditya003@gmail.com"
SMTP_PASSWORD = "uahn katp kxvl nkkx"

def load_json(file_path):
    """Load JSON data from a file."""
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def send_email(to_email, subject, body):
    """Send an email to a user."""
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_USERNAME
        msg["To"] = to_email

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to_email, msg.as_string())

        print(f"✅ Email sent to {to_email}: {subject}")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")

def send_event_reminders():
    """Send reminders for events."""
    events = load_json(EVENTS_FILE)
    registrations = load_json(REGISTRATIONS_FILE)

    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)

    for reg in registrations:
        event_id = reg["event_id"]
        user_email = reg["user_email"]
        
        event = events.get(event_id)
        if not event:
            continue

        event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()

        # Send event-day reminder
        if event_date == today:
            send_email(user_email, "📢 Event Today!", f"Your event '{event['name']}' is happening today at {event['location']}! Don't forget to attend.")

        # Send before-event reminder
        elif event_date == tomorrow:
            send_email(user_email, "⏳ Event Reminder", f"Your event '{event['name']}' is happening tomorrow! Prepare yourself!")

if __name__ == "__main__":
    send_event_reminders()

