import json
import smtplib
from email.mime.text import MIMEText

# File Paths
EVENTS_FILE = "/home/user/data/events.json"
ANNOUNCEMENTS_FILE = "/home/user/data/announcements.json"
USERS_FILE = "/home/user/data/users.json"
TRACKING_FILE = "/home/user/data/last_update.json"

# Email Config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "panalaaditya003@gmail.com"
SMTP_PASSWORD = "uahn katp kxvl nkkx"

# Load JSON Files
def load_json(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save JSON Files
def save_json(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

# Send Email Function
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
        print(f"❌ Error sending email: {e}")

# Notify Users about New Events & Announcements
def notify_new_updates():
    events = load_json(EVENTS_FILE)
    announcements = load_json(ANNOUNCEMENTS_FILE)
    users = load_json(USERS_FILE)
    last_update = load_json(TRACKING_FILE)

    last_event_count = last_update.get("event_count", 0)
    last_announcement_count = last_update.get("announcement_count", 0)

    current_event_count = len(events)
    current_announcement_count = len(announcements)

    new_events = current_event_count > last_event_count
    new_announcements = current_announcement_count > last_announcement_count

    if new_events or new_announcements:
        for user_email in users.keys():
            if new_events:
                send_email(user_email, "🚀 New Event Added!", "A new event has been added. Check the website for details.")
            if new_announcements:
                send_email(user_email, "📢 New Announcement!", "A new announcement has been posted. Visit the website to read it.")

        # Update tracking file
        last_update["event_count"] = current_event_count
        last_update["announcement_count"] = current_announcement_count
        save_json(TRACKING_FILE, last_update)

if __name__ == "__main__":
    notify_new_updates()
