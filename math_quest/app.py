from flask import Flask, render_template, request, redirect, url_for, session, flash
from math import isclose

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "supersecretkey"

# Define the 10 levels with their names, descriptions, and questions
levels = [
    {"name": "Level 1: Basics", "description": "Start your journey with basic puzzles!", "questions": [
        {"question": "What is 5 + 3?", "answer": "8"},
        {"question": "What is 10 - 4?", "answer": "6"}
    ]},
    {"name": "Level 2: Multiplication", "description": "Test your multiplication skills!", "questions": [
        {"question": "What is 6 x 7?", "answer": "42"},
        {"question": "What is 8 x 8?", "answer": "64"}
    ]},
    # Define levels 3 to 10 in the same format
]

# Track team progress (team_name -> level index, score, and completion status)
team_progress = {}

@app.route("/", methods=["GET", "POST"])
def home():
    """Home page for team registration."""
    if request.method == "POST":
        team_name = request.form["team_name"]
        session["team_name"] = team_name
        team_progress[team_name] = {"current_level": 0, "completed_levels": [], "score": 0, "question_index": 0}
        return redirect(url_for("dashboard"))
    return render_template("home.html")

@app.route("/dashboard")
def dashboard():
    """Dashboard showing levels and team progress."""
    team_name = session.get("team_name")
    if not team_name or team_name not in team_progress:
        return redirect(url_for("home"))

    progress = team_progress[team_name]
    return render_template(
        "dashboard.html",
        levels=levels,
        progress=progress,
        team_name=team_name,
        all_teams=team_progress
    )

@app.route("/level/<int:level_id>", methods=["GET", "POST"])
def level(level_id):
    """Level page for the selected level."""
    team_name = session.get("team_name")
    if not team_name or team_name not in team_progress:
        return redirect(url_for("home"))

    progress = team_progress[team_name]
    current_level = progress["current_level"]

    # Ensure the level is unlocked for the team (can only access the current or previous levels)
    if level_id > current_level:
        flash("You need to complete previous levels first!", "danger")
        return redirect(url_for("dashboard"))

    level_data = levels[level_id]
    questions = level_data["questions"]

    # Track question progress and score within the level
    if "question_index" not in progress:
        progress["question_index"] = 0
        progress["score"] = 0  # Reset score for the level

    question_index = progress["question_index"]

    # Check if all questions are completed
    if question_index >= len(questions):
        total_questions = len(questions)
        passing_score = total_questions / 2  # Minimum score to pass is 50%

        # If score is more than passing score, move to next level
        if progress["score"] > passing_score:
            progress["completed_levels"].append(level_id)
            progress["current_level"] = level_id + 1  # Unlock next level
            progress["question_index"] = 0  # Reset for the next level
            progress["score"] = 0  # Reset score for the next level
            flash(f"Congratulations! You've completed {level_data['name']} with a score of {progress['score']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash(f"Sorry, you did not pass {level_data['name']} (Score: {progress['score']}). It's a dead end!", "danger")
            progress["question_index"] = 0  # Reset the level
            progress["score"] = 0  # Reset score
            return redirect(url_for("dashboard"))

    # Handle form submission
    if request.method == "POST":
        answer = request.form["answer"].strip()

        # Get the correct answer
        correct_answer = questions[question_index]["answer"]

        # Flexible answer checking
        if isinstance(correct_answer, (int, float)):
            # Numerical answer: Check with tolerance
            if isclose(float(answer), correct_answer, abs_tol=1):
                progress["score"] += 1
                flash("Correct! Moving to the next question.", "success")
            else:
                flash("Incorrect! Try again.", "danger")
        else:
            # String answer: Case-insensitive match
            if answer.lower() == correct_answer.lower():
                progress["score"] += 1
                flash("Correct! Moving to the next question.", "success")
            else:
                flash("Incorrect! Try again.", "danger")

        # Move to the next question
        progress["question_index"] += 1

    # Show the current question
    current_question = questions[question_index]
    return render_template(
        "level.html",
        level_name=level_data["name"],
        question=current_question["question"],
        question_number=question_index + 1,
        total_questions=len(questions),
        score=progress["score"]
    )

@app.route("/reset")
def reset():
    """Reset the session."""
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
