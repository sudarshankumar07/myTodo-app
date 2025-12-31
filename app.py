from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# ---------------- APP SETUP ----------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")


# ---------------- DATABASE ----------------
def get_db_connection():
    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor
    )


def init_db():
    db = get_db_connection()
    cur = db.cursor()

    # USERS TABLE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    """)

    # TODO TABLE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS todo (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            task TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    db.commit()
    cur.close()
    db.close()


init_db()

# ---------------- PAGES ----------------
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("mytodo.html")


@app.route("/login_page")
def login_page():
    return render_template("login.html")


@app.route("/register_page")
def register_page():
    return render_template("register.html")


# ---------------- AUTH ----------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not all([name, email, password]):
        return jsonify({"error": "Missing fields"}), 400

    hashed = generate_password_hash(password)

    try:
        db = get_db_connection()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO users (name,email,password) VALUES (%s,%s,%s)",
            (name, email, hashed)
        )
        db.commit()
        return jsonify({"success": True})

    except psycopg2.IntegrityError:
        db.rollback()
        return jsonify({"error": "Email already exists"}), 409

    except psycopg2.Error as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        db.close()


@app.route("/user-login", methods=["POST"])
def user_login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    email = data.get("email")
    password = data.get("password")

    try:
        db = get_db_connection()
        cur = db.cursor()
        cur.execute(
            "SELECT id, password FROM users WHERE email=%s",
            (email,)
        )
        user = cur.fetchone()

    finally:
        cur.close()
        db.close()

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    session["user_id"] = user["id"]
    return jsonify({"success": True})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


# ---------------- PROFILE ----------------
@app.route("/api/profile")
def profile():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db_connection()
    cur = db.cursor()
    cur.execute(
        "SELECT name, email FROM users WHERE id=%s",
        (session["user_id"],)
    )
    user = cur.fetchone()
    cur.close()
    db.close()

    return jsonify(user)


# ---------------- ADD TASK ----------------
@app.route("/api/add
