import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from extensions import bcrypt
from otp import initiate_otp_flow
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta

auth = Blueprint('auth', __name__)
DB_NAME = "plates.db"

def get_db():
    conn = sqlite3.connect("plates.db")
    conn.row_factory = sqlite3.Row
    return conn

@auth.route("/register", methods=["GET", "POST"])
def register():
    error = None
    success = None

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not username or not password:
            error = "Please enter both username and password."
            return render_template("register.html", error=error)

        # Connect to DB and check for duplicate username
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE LOWER(username) = ?", (username,))
        existing_user = cursor.fetchone()
        conn.close()

        if existing_user:
            error = "Username already exists. Please choose another."
            return render_template("register.html", error=error)

        # Proceed with OTP if username is available
        session["reg_username"] = username
        session["reg_password"] = password

        initiate_otp_flow()
        return redirect(url_for("auth.verify_otp"))

    return render_template("register.html", error=error, success=success)


@auth.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username").strip().lower()
        password = request.form.get("password")

        try:
            # Connect to the database
            conn = sqlite3.connect(DB_NAME)
            conn.row_factory = sqlite3.Row  # Enables dictionary-style row access
            cursor = conn.cursor()

            # Fetch user with password and role
            cursor.execute("SELECT password, role FROM users WHERE LOWER(username) = LOWER(?)",(username,))
            user = cursor.fetchone()
            conn.close()

            # Validate user and password
            if user and check_password_hash(user["password"], password):
                #print("Raw DB row:", dict(user))  # ✅ Shows exactly what's being returned
                session["user"] = username
                session["role"] = user["role"]
                print(f"[LOGIN SUCCESS] {username} logged in with role: {session['role']}")
                return redirect(url_for("index"))

            else:
                error = "Invalid username or password."

        except Exception as e:
            error = f"Login error: {str(e)}"
            print(f"[LOGIN ERROR] {error}")  # Optional debug

    return render_template("login.html", error=error)

@auth.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        expected_otp = session.get("otp")
        sent_time = session.get("otp_sent_at")

        # Check if OTP is expired
        if sent_time:
            sent_at = datetime.fromisoformat(sent_time)
            if datetime.utcnow() > sent_at + timedelta(minutes=30):
                session.pop("otp", None) 
                session.pop("otp_sent_at", None) # Clears expired OTP's from session
                flash("OTP has expired. Please request a new one.", "warning")
                return redirect(url_for("auth.resent_otp"))

        if entered_otp == expected_otp:
            # Clean up OTP from session
            session.pop('otp', None)

            # Get user info from session
            username = session.pop("reg_username", None)
            password = session.pop("reg_password", None)

            if not username or not password:
                flash("Missing user information. Please try registering again.", "danger")
                return redirect(url_for("auth.register"))
            
            # Save user to DB
            try:
                db = sqlite3.connect(DB_NAME)
                cursor = db.cursor()

                hashed_pw = generate_password_hash(password)

                cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (username, hashed_pw, "user")  # default role
                )

                db.commit()
                db.close()

                flash("Account created successfully! You can now log in.", "success")
                return redirect(url_for("auth.login"))

            except sqlite3.IntegrityError:
                flash("That username already exists. Try logging in.", "danger")
                return redirect(url_for("auth.login"))
            except Exception as e:
                flash(f"Error creating user: {e}", "danger")
                return redirect(url_for("auth.register"))
        else:
            flash("Incorrect OTP. Please try again.", "danger")

    return render_template("verify_otp.html")

@auth.route("/resend-otp")
def resend_otp():
    try:
        initiate_otp_flow()
        flash("A new OTP has been sent to the admin phone number.", "info")
    except Exception as e:
        flash(f"Failed to resend OTP: {str(e)}", "danger")
    return redirect(url_for("auth.verify_otp"))

@auth.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("auth.login"))
