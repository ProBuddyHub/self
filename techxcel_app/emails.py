'''
from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

# 🔹 Replace these with your actual email server details
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # e.g., smtp.yourdomain.com
app.config['MAIL_PORT'] = 587  # or 465 for SSL
app.config['MAIL_USE_TLS'] = True  # False if using SSL
app.config['MAIL_USE_SSL'] = False  # True if using SSL
app.config['MAIL_USERNAME'] = 'panalaaditya003@gmail.com'
app.config['MAIL_PASSWORD'] = 'uahn katp kxvl nkkx'  # Use App Password if applicable
app.config['MAIL_DEFAULT_SENDER'] = 'panalaaditya003@gmail.com'

mail = Mail(app)

def send_test_email():
    with app.app_context():
        try:
            recipient_email = "panalaaditya@gmail.com"  # Change to any email you want to test
            msg = Message('Test Email', recipients=[recipient_email])
            msg.body = 'This is a test email from Flask-Mail.'

            mail.send(msg)
            print(f"✅ Test email sent to {recipient_email} successfully!")
        except Exception as e:
            print(f"❌ Error sending email: {e}")

# Run the test
if __name__ == "__main__":
    send_test_email()
'''

from flask_mail import Mail, Message
from flask import Flask, url_for
import secrets  # For generating unique confirmation tokens

app = Flask(__name__)

# 🔹 Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'panalaaditya003@gmail.com'
app.config['MAIL_PASSWORD'] = 'uahn katp kxvl nkkx'
app.config['MAIL_DEFAULT_SENDER'] = 'panalaaditya003@gmail.com'

mail = Mail(app)

def generate_confirmation_token():
    """Generate a unique confirmation token."""
    return secrets.token_urlsafe(32)

def send_confirmation_email(user_email):
    """Send a confirmation email with a verification link."""
    with app.app_context():
        try:
            token = generate_confirmation_token()
            confirmation_url = url_for('confirm_email', token=token, _external=True)
            subject = "Confirm Your Email - TechXcel Event Management"
            body = f"Click the link to confirm your email: {confirmation_url}"

            msg = Message(subject, recipients=[user_email])
            msg.body = body
            mail.send(msg)
            
            print(f"✅ Confirmation email sent to {user_email}")
            return token  # Return token to store in the database (or temporary storage)
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return None
