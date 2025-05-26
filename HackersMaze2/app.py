import os
import json
import hashlib
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a strong secret key

# Use relative paths so that users.json and forgot.json are in the same directory as app.py
BASE_DIR = os.path.dirname(__file__)
USER_FILE = os.path.join(BASE_DIR, 'users.json')
FORGOT_FILE = os.path.join(BASE_DIR, 'forgot.json')

# --- Utility Functions ---
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
            return data
    return {}

def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    return load_json(USER_FILE)

def save_users(users):
    save_json(USER_FILE, users)

# --- Routes for HTML Pages ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    user_email = session['user']
    users = load_users()
    user = users.get(user_email, {})
    return render_template('dashboard.html', username=user.get('username', user_email))

# (Other routes like /profile, /levels, etc. can remain as needed.)

# --- API Endpoints ---
@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.get_json()
    username = data.get('username')
    branch = data.get('branch')
    year = data.get('year')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, branch, year, email, password]):
        return jsonify({"message": "Missing fields"}), 400
    
    users = load_users()
    if email in users:
        return jsonify({"message": "Email already registered"}), 400

    users[email] = {
        "username": username,
        "branch": branch,
        "year": year,
        "email": email,
        "password": hash_password(password)
    }
    save_users(users)
    return jsonify({"message": "Signup successful"}), 201

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"message": "Missing email or password"}), 400
    
    users = load_users()
    hashed_input = hash_password(password)
    
    # Debug logging (you can remove these in production)
    print(f"Attempting login for: {email}")
    print(f"Input password hash: {hashed_input}")
    if email in users:
        print(f"Stored password hash: {users[email]['password']}")
    
    if email in users and users[email]['password'] == hashed_input:
        session['user'] = email
        return jsonify({"message": "Login successful", "username": users[email].get("username")}), 200
    else:
        print("Login failed: Invalid credentials")
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/forgot', methods=['POST'])
def api_forgot():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"message": "Email is required"}), 400
    
    forgot_data = load_json(FORGOT_FILE)
    forgot_data[email] = {"request": "Password reset requested"}
    save_json(FORGOT_FILE, forgot_data)
    
    return jsonify({"message": "Password reset request received. Check your email for further instructions."}), 200


@app.route('/levels')
def levels():
    return render_template('level.html')


@app.route('/level_1')
def level_1():
    return render_template('level_1.html')

@app.route('/level_2')
def level_2():
    return render_template('level_2.html')

@app.route('/level_3')
def level_3():
    return render_template('level_3.html')

@app.route('/level_4')
def level_4():
    return render_template('level_4.html')

@app.route('/level_5')
def level_5():
    return render_template('level_5.html')

@app.route('/level_6')
def level_6():
    return render_template('level_6.html')

@app.route('/level_7')
def level_7():
    return render_template('level_7.html')

@app.route('/level_8')
def level_8():
    return render_template('level_8.html')

@app.route('/level_9')
def level_9():
    return render_template('level_9.html')

@app.route('/level_10')
def level_10():
    return render_template('level_10.html')


@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    user_email = session['user']
    users = load_users()
    user = users.get(user_email, {})  # Get user data safely

    # Ensure all required fields exist, else provide default values
    user_data = {
        "username": user.get("username", "N/A"),
        "branch": user.get("branch", "N/A"),
        "year": user.get("year", "N/A"),
        "email": user.get("email", user_email)
    }

    return render_template('profile.html', user=user_data)

@app.route('/edit_profile')
def edit_profile():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    user_email = session['user']
    users = load_users()
    user = users.get(user_email, {})

    user_data = {
        "username": user.get("username", ""),
        "branch": user.get("branch", ""),
        "year": user.get("year", ""),
        "email": user.get("email", user_email)  # Email should not be editable
    }
    return render_template('edit_profile.html', user=user_data)


@app.route('/api/edit_profile', methods=['POST'])
def api_edit_profile():
    if 'user' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    user_email = session['user']
    users = load_users()

    if user_email not in users:
        return jsonify({"message": "User not found"}), 404

    # Get new values from the form
    username = request.form.get('username')
    branch = request.form.get('branch')
    year = request.form.get('year')

    if not all([username, branch, year]):
        return jsonify({"message": "Missing fields"}), 400

    # Update user details
    users[user_email]['username'] = username
    users[user_email]['branch'] = branch
    users[user_email]['year'] = year

    save_users(users)
    return redirect(url_for('profile'))


@app.route('/instructions')
def instructions():
    return render_template('instructions.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login_page'))

# --- App Initialization ---
if __name__ == '__main__':
    # Create the JSON files if they do not exist.
    if not os.path.exists(USER_FILE):
        save_users({})
    if not os.path.exists(FORGOT_FILE):
        save_json(FORGOT_FILE, {})
    app.run(debug=True, port=5000)
