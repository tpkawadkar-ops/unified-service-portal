from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- USERS ----------------
USERS = {
    "user": {"password": "user123", "role": "user"},
    "admin": {"password": "admin123", "role": "admin"}
}

# ---------------- DB HELPER ----------------
def get_db():
    conn = sqlite3.connect("database.db")
    return conn

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in USERS and USERS[username]["password"] == password:
            session["role"] = USERS[username]["role"]
            session["user"] = username
            return redirect("/dashboard")

    return render_template("login.html")

# ---------------- DASHBOARD ROUTER ----------------
@app.route("/dashboard")
def dashboard():
    if "role" not in session:
        return redirect("/")

    if session["role"] == "admin":
        return redirect("/admin")

    return render_template("user_dashboard.html")

# ---------------- USER SUBMIT REQUEST ----------------
@app.route("/submit", methods=["POST"])
def submit():
    if "role" not in session or session["role"] != "user":
        return redirect("/")

    db = get_db()
    db.execute("""
        INSERT INTO requests (title, category, priority, status, requester, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        request.form["title"],
        request.form["category"],
        request.form["priority"],
        "Submitted",
        session["user"],
        datetime.now()
    ))
    db.commit()
    db.close()

    return redirect("/dashboard")

# ---------------- USER: MY REQUESTS ----------------
@app.route("/my-requests")
def my_requests():
    if "role" not in session or session["role"] != "user":
        return redirect("/")

    db = get_db()
    data = db.execute(
        "SELECT * FROM requests WHERE requester=?",
        (session["user"],)
    ).fetchall()
    db.close()

    return render_template("my_requests.html", requests=data)

# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
def admin():
    if "role" not in session or session["role"] != "admin":
        return redirect("/")

    db = get_db()
    requests_data = db.execute("SELECT * FROM requests").fetchall()
    counts = db.execute(
        "SELECT status, COUNT(*) FROM requests GROUP BY status"
    ).fetchall()
    db.close()

    return render_template(
        "admin_dashboard.html",
        requests=requests_data,
        counts=counts
    )

# ---------------- ADMIN UPDATE STATUS ----------------
@app.route("/update-status", methods=["POST"])
def update_status():
    if "role" not in session or session["role"] != "admin":
        return redirect("/")

    req_id = request.form["request_id"]
    status = request.form["status"]

    db = get_db()
    db.execute(
        "UPDATE requests SET status=? WHERE id=?",
        (status, req_id)
    )
    db.commit()
    db.close()

    return redirect("/admin")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
