import sqlite3
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from db import log_action

admin = Blueprint('admin', __name__)
DB_NAME = "plates.db"

@admin.route("/admin/users")
def manage_users():
    if session.get("role") != "admin":
        return redirect(url_for("index"))

    conn = sqlite3.connect("plates.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()
    conn.close()

    return render_template("user_management.html", users=users)

@admin.route("/admin/update-role", methods=["POST"])
def update_user_role():
    if session.get("role") != "admin":
        return redirect(url_for("index"))

    username = request.form.get("username")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        new_role = "user" if user[0] == "admin" else "admin"
        cursor.execute("UPDATE users SET role = ? WHERE username = ?", (new_role, username))
        conn.commit()
        log_action(session.get("user"), f"{'Promoted' if new_role == 'admin' else 'Demoted'} user", username)
        flash(f"{username} has been updated to {new_role}.", "success")
    else:
        flash("User not found.", "danger")

    conn.close()
    return redirect(url_for("admin.manage_users"))

@admin.route("/admin/delete-user", methods=["POST"])
def delete_user():
    if session.get("role") != "admin":
        return redirect(url_for("index"))

    username = request.form.get("username")

    # Prevent deleting yourself
    if username == session.get("user"):
        flash("You cannot delete your own account while logged in.", "danger")
        return redirect(url_for("admin.manage_users"))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    log_action(session.get("user"), "Deleted user", username)
    conn.close()

    flash(f"User {username} has been deleted.", "success")
    return redirect(url_for("admin.manage_users"))

@admin.route("/admin/audit-log")
def view_audit_log():
    if session.get("role") != "admin":
        return redirect(url_for("index"))

    username = request.args.get("username")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT action, details, timestamp FROM audit_logs WHERE username = ? ORDER BY timestamp DESC", (username,))
    logs = cursor.fetchall()
    conn.close()

    return render_template("audit_log.html", username=username, logs=logs)

@admin.route("/admin/settings", methods=["GET", "POST"])
def admin_settings():
    if session.get("role") != "admin":
        return redirect(url_for("index"))

    success = None
    error = None
    phone = ""

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if request.method == "POST":
        phone = request.form.get("otp_phone")
        try:
            cursor.execute("DELETE FROM otp_settings")
            cursor.execute("INSERT INTO otp_settings (phone) VALUES (?)", (phone,))
            conn.commit()
            log_action(session.get("user"), "Updated OTP phone", phone)
            success = "OTP phone number updated successfully."
        except Exception as e:
            error = f"Error saving phone number: {str(e)}"
    else:
        cursor.execute("SELECT phone FROM otp_settings ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        phone = result[0] if result else ""

    conn.close()
    return render_template("settings.html", phone=phone, success=success, error=error)