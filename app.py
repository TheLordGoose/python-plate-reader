import re
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from db import init_db, get_all_plates, add_plate, delete_plate, log_action
from flask import send_file
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from flask_bcrypt import bcrypt
from extensions import bcrypt
from admin import admin
from utils import normalize_plate, is_valid_uk_plate


app = Flask(__name__)
app.register_blueprint(admin)
app.secret_key = os.urandom(24)

bcrypt.init_app(app)

from auth import auth
app.register_blueprint(auth)


# In-memory storage for plates (resets on restart)
plates = []

MAX_PLATES = 10

# Initialise the db
init_db()

# Adds the plates to the DB, with validation checking.
@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    
    is_admin = session.get("role") == "admin"
    
    success = None
    error = None
    warning = None
    phone = None

    db = sqlite3.connect("plates.db")
    cursor = db.cursor()

    if request.method == "POST":
        if "plate" in request.form:  # Plate submission
            new_plate = request.form.get("plate", "").strip().upper()
            print(f"New plate from form: {new_plate}")

            if is_valid_uk_plate(new_plate):
                try:
                    add_plate(new_plate)
                    log_action(session.get("user"), "Added plate", new_plate)
                    success = f"Plate {new_plate} added successfully!"
                except ValueError as e:
                    warning = str(e)
                except Exception as e:
                    error = f"Error adding plate: {str(e)}"
            else:
                error = "Invalid UK licence plate format."

        elif "otp_phone" in request.form:  # Admin setting OTP phone number
            new_phone = request.form.get("otp_phone", "").strip()
            if new_phone:
                try:
                    cursor.execute("DELETE FROM otp_settings")
                    cursor.execute("INSERT INTO otp_settings (phone) VALUES (?)", (new_phone,))
                    db.commit()
                    success = "OTP phone number updated successfully!"
                except Exception as e:
                    error = f"Failed to save phone number: {str(e)}"

    # Get the current stored phone number
    try:
        cursor.execute("SELECT phone FROM otp_settings LIMIT 1")
        row = cursor.fetchone()
        if row:
            phone = row[0]
    except:
        phone = None  # In case the table doesn't exist yet

    db.close()

    plates = get_all_plates()
    print(plates)
    return render_template(
        "index.html",
        plates=plates,
        success=success,
        error=error,
        warning=warning,
        phone=phone,
        is_admin=is_admin
    )

# Deletes the plates from the db
@app.route("/delete/<plate>", methods=["GET"])
def delete_plate_route(plate):
    if "user" not in session:
        return redirect(url_for("auth.login"))
    delete_plate(plate)
    log_action(session.get("user"), "Deleted plate", plate)
    return redirect(url_for("index"))

"""@app.route("/scan_plate", methods=["POST"])
def scan_plate():
    import cv2
    import pytesseract
    import numpy as np
    from PIL import Image
    from db import get_all_plates, normalize_plate
    from flask import request, jsonify

    # Check if image was uploaded
    file = request.files.get("image")
    if not file:
        return jsonify({"success": False, "message": "No image received."})

    # Read uploaded image into OpenCV format
    npimg = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"success": False, "message": "Failed to decode uploaded image."})

    # OPTIONAL: Resize frame
    frame = cv2.resize(frame, (640, 480))

    # Crop region (ROI)
    h, w, _ = frame.shape
    roi_x1 = int(w * 0.25)
    roi_y1 = int(h * 0.4)
    roi_x2 = int(w * 0.75)
    roi_y2 = int(h * 0.6)
    plate_roi = frame[roi_y1:roi_y2, roi_x1:roi_x2]

    # Save for debugging
    cv2.imwrite("debug_ocr_input.jpg", plate_roi)

    # Set tesseract path (if needed)
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    # Preprocessing
    gray = cv2.cvtColor(plate_roi, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    resized = cv2.resize(thresh, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    img_pil = Image.fromarray(resized)

    # OCR with whitelist
    raw_text = pytesseract.image_to_string(
        img_pil,
        config="--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    )

    # Normalize detected plate
    plate_text = normalize_plate(raw_text)
    print(f"[OCR] Detected raw: {raw_text} | Normalized: {plate_text}")

    # Get and normalize stored plates
    stored_plates = get_all_plates()
    normalized_plates = [normalize_plate(p) for p in stored_plates]
    print("Stored plates:", normalized_plates)

    # Match
    if plate_text in normalized_plates:
        return jsonify({"success": True, "message": f"✅ Plate matched: {plate_text}"})
    else:
        return jsonify({"success": False, "message": f"❌ Plate not found: {plate_text}"})"""

@app.route("/scan_plate", methods=["POST"])
def scan_plate():
    import cv2
    import pytesseract
    import numpy as np
    from PIL import Image
    from db import get_all_plates
    from utils import normalize_plate  # Make sure this is defined and imported
    from flask import request, jsonify

    file = request.files.get("image")
    if not file:
        return jsonify({"success": False, "message": "No image received."})

    npimg = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"success": False, "message": "Failed to decode image."})

    # Crop ROI - match your HTML overlay
    h, w, _ = frame.shape
    roi = frame[int(h * 0.4):int(h * 0.6), int(w * 0.25):int(w * 0.75)]

    # Preprocessing
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    resized = cv2.resize(thresh, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

    # OCR
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    img_pil = Image.fromarray(resized)
    raw_text = pytesseract.image_to_string(
        img_pil,
        config="--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    )

    # Normalize text
    plate_text = normalize_plate(raw_text)
    print(f"[OCR] Raw: {repr(raw_text)}")
    print(f"Normalized: {repr(plate_text)}")

    # Fetch and normalize all plates from DB
    stored_plates = [normalize_plate(p) for p in get_all_plates()]
    print("Stored (normalized):", [repr(p) for p in stored_plates])

    if plate_text in stored_plates:
        return jsonify({"success": True, "message": f"✅ Plate matched: {plate_text}"})
    else:
        return jsonify({"success": False, "message": f"❌ Plate not found: {plate_text}"})


# DO NOT PUT ANYTHING BELOW THIS
if __name__ == "__main__":
    app.run(debug=True)
