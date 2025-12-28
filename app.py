from flask import Flask, render_template, session, request, jsonify, redirect, url_for
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# SECRET KEY (Render ENV)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret")


# ---------------- HOME ----------------
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect("/reg_log")
    return render_template("myTodo.html")


@app.route("/reg_log")
def reg_log():
    return render_template("index.html")


# ---------------- TEST API ----------------
@app.route("/api/data", methods=["POST"])
def data():
    data = request.json
    return jsonify({"message": f"Hello {data['name']}"})


# ---------------- AUTH PAGES ----------------
@app.route("/login_page")
def login_page():
    return render_template("login.html")


@app.route("/register_page")
def register_page():
    return render_template("register.html")


@app.route("/api/login", methods=["POST"])
def login():
    return jsonify(success=True, redirect="/login_page")


@app.route("/api/register", methods=["POST"])
def register():
    return jsonify(success=True, redirect="/register_page")


# ---------------- DB CONNECTION (RENDER SAFE) ----------------
def get_db_connection():
    return pymysql.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME"),
        port=int(os.environ.get("DB_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"success": False, "message": "Missing fields"}), 400

    hashed = generate_password_hash(password)

    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed)
        )
        return jsonify({"success": True, "redirect": "/login_page"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        db.close()


# ---------------- LOGIN ----------------
@app.route("/user-login", methods=["POST"])
def userLogin():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute(
            "SELECT id, password FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        if not check_password_hash(user["password"], password):
            return jsonify({"error": "Wrong password"}), 401

        session["user_id"] = user["id"]
        return jsonify({"success": True, "redirect": "/todo"})
    finally:
        cursor.close()
        db.close()


# ---------------- SESSION CHECK ----------------
@app.route("/api/session")
def check_session():
    if "user_id" not in session:
        return {"logged_in": False}, 401

    return {"logged_in": True, "user_id": session["user_id"]}


# ---------------- TODO PAGE ----------------
@app.route("/todo")
def todo():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("myTodo.html")


# ---------------- PROFILE ----------------
@app.route("/api/profile")
def profile():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute(
            "SELECT name, email FROM users WHERE id = %s",
            (session["user_id"],)
        )
        return jsonify(cursor.fetchone())
    finally:
        cursor.close()
        db.close()


# ---------------- ADD TASK ----------------
@app.route("/api/add_task", methods=["POST"])
def addTask():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid JSON"}), 400

    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT INTO todo (user_id, title, task, description) VALUES (%s, %s, %s, %s)",
            (
                session["user_id"],
                data.get("title"),
                data.get("task"),
                data.get("description", "")
            )
        )
        return jsonify({"success": True}), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        db.close()


# ---------------- SHOW TASKS ----------------
@app.route("/api/show_task", methods=["GET"])
def show_task():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute(
            "SELECT id, title, task, description FROM todo WHERE user_id = %s ORDER BY id DESC",
            (session["user_id"],)
        )
        return jsonify({"success": True, "tasks": cursor.fetchall()})
    finally:
        cursor.close()
        db.close()


# ---------------- LOGOUT ----------------
@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify(success=True, redirect="/login_page")
