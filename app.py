from flask import Flask, render_template, session, request, jsonify,redirect , session, url_for
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash




#__HOME PAGE RENDER
app = Flask(__name__)
app.secret_key = "dev-secret-key"
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect("/reg_log")
    return render_template("myTOdo.html")

@app.route("/reg_log")
def reg_log():
    return render_template("index.html")
#__CHECKING CONNECTION BETWEEN JS AND FLASK
@app.route("/api/data",methods=["POST"])
def data():
    data = request.json
    return jsonify({"message":f"Hello {data['name']}"
    })

#__ROUTE FOR LOGIN PAGE
@app.route("/login_page")
def login_page():
    return render_template("login.html")


#__ROUTE FOR REGISTER PAGE
@app.route("/register_page")
def register_page():
    return render_template("register.html")

#__ANYONE CLICK LOGIN BTN IT WILL REDIRECT TO LOGIN PAGE
@app.route("/api/login", methods=["POST"])
def login():
    return jsonify(success = True, redirect="/login_page")

#__ANYONE CLICK REGISTER BTN IT WILL REDIRECT TO REGISTER PAGE
@app.route("/api/register", methods=["POST"])
def register():
    return jsonify(success = True, redirect="/register_page")


#__CONNECT MYSQL WITH FLASK
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="73038",
        database="testdb",
        port=3306,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

#__CREATE A API THAT TAKE USER DATA AND STORE THEM IN DATA BASE AND RETURN PROMISE AND IF IT SUCCESSFULL
#__JS WILL REDIRECT TO LOGIN PAGE
@app.route("/signup",methods=["POST"])
def signup():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    hashed = generate_password_hash(password)

    if not name or not email or not password:
        return jsonify({"success": False, "message": "Missing fields"}), 400

    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed)
        )
        db.commit() 
        return jsonify({"success": True, "redirect": "/login_page"})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        db.close()

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

@app.route("/api/session")
def check_session():
    if "user_id" not in session:
        return{"logged_in":False},401
    return{
        "logged_in":True,
        "user_id": session["user_id"]
    }

@app.route("/todo")
def todo():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("myTodo.html")

@app. route("/api/profile")
def profile():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    db = get_db_connection()
    cursor = db.cursor()
    user_id = session['user_id']
    cursor.execute(
            "SELECT DISTINCT name , email FROM users WHERE id= %s",(user_id) )
    user = cursor.fetchone()
    db.close()
    return jsonify(user)


@app.route("/api/add_task", methods = ["POST"])
def addTask():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success":False,"error":"Invalid Json"}),400
    title = data.get("title")
    task = data.get("task")
    description = data.get("description","")
    db =get_db_connection()
    cursor = db.cursor()
    try:
        user_id = session['user_id']
        cursor.execute(
            "INSERT INTO todo (user_id,title,task,description) VALUES (%s,%s,%s,%s)",
            (user_id,title,task,description)
        )
        db.commit()
        return jsonify({"success": True}),201
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        db.close()

@app.route("/api/show_task", methods=["GET"])
def show_task():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT id, title, task, description FROM todo WHERE user_id = %s ORDER BY id DESC",
            (user_id,)
        )
        task = cursor.fetchall()
        return jsonify({"success": True,"tasks":task}),200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        db.close()

@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop('user_id',None)
    return jsonify(success = True, redirect="/login_page")


if __name__ == "__main__":
    app.run(debug=True)


