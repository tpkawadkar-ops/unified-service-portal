from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime
from flask import redirect



app = Flask(__name__)
app.secret_key = "secretkey"

def get_db():
    return sqlite3.connect("database.db")


USERS = {
    "user": {"password": "user123", "role": "user"},
    "admin": {"password": "admin123", "role": "admin"}
}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in USERS and USERS[username]["password"] == password:
            session["role"] = USERS[username]["role"]
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if session.get("role") == "admin":
        return redirect("/admin")
    return render_template("user_dashboard.html")


@app.route("/submit", methods=["POST"])
def submit_request():
    db = get_db()
    db.execute("""
        INSERT INTO requests
        (title, category, priority, status, requester, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        request.form["title"],
        request.form["category"],
        request.form["priority"],
        "Submitted",
        "user",
        datetime.now()
    ))
    db.commit()
    return redirect("/dashboard")

@app.route("/admin")
def admin_view():
    db = get_db()

    # Fetch all requests
    requests_data = db.execute(
        "SELECT * FROM requests"
    ).fetchall()

    # Fetch count of requests by status
    counts = db.execute(
        "SELECT status, COUNT(*) FROM requests GROUP BY status"
    ).fetchall()

    return render_template(
        "admin_dashboard.html",
        requests=requests_data,
        counts=counts
    )


@app.route("/my-requests")
def my_requests():
    db = get_db()
    data = db.execute(
        "SELECT * FROM requests WHERE requester='user'"
    ).fetchall()
    return render_template("my_requests.html", requests=data)


if __name__ == "__main__":
    app.run(debug=True)
