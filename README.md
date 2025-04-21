# 🏷️ Python Plate Reader

A full-stack Flask web app for scanning and managing UK vehicle license plates using OCR and webcam integration. Built with Flask, OpenCV, Tesseract, and Twilio for OTP verification.

![screenshot](static/assets/preview.png)

---

## 🚀 Features

- 📷 Scan plates using a webcam with live OCR  
- 🔒 OTP-based registration with phone verification (Twilio)  
- 🧠 UK plate format validation  
- 📄 Audit logs for user actions  
- 🔐 User authentication with roles (admin/user)  
- 📱 Admin-only phone number settings  
- 👮 Admin user management panel  
- 🕵️ Duplicate plate detection & normalization (e.g., "AB12 XYZ" vs "AB12XYZ")  
- 📦 Secure `.env` usage for credentials  

---

## 🛠️ Tech Stack

- **Backend:** Flask, SQLite, Tesseract OCR  
- **Frontend:** HTML, Bootstrap, JavaScript (webcam capture, live input)  
- **Auth & Security:** Flask sessions, password hashing, OTP (Twilio)  
- **OCR Engine:** Tesseract (via `pytesseract`)  
- **Image Processing:** OpenCV  

---

## 📦 Installation

```bash
git clone https://github.com/YOUR_USERNAME/python-plate-reader.git
cd python-plate-reader
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory with:

```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+447123456789
```

---

## ▶️ Running the App

```bash
python app.py
```

App will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🔍 Tesseract Setup (Windows)

Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) and set this path in your code (already configured in the app):

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

---

## 🔐 Admin Tips

- Admins can:
  - Manage users
  - Set the OTP phone number
  - Access plate scan features  
- Regular users can only add/remove plates.

---

## 📸 How Plate Scanning Works

1. Webcam captures a frame  
2. ROI (Region of Interest) isolates the plate  
3. Image is preprocessed (grayscale, threshold, CLAHE)  
4. OCR extracts text  
5. Normalized plate is compared to stored plates  

---

## 📁 Folder Structure

```
├── app.py
├── db.py
├── auth.py
├── admin.py
├── otp.py
├── utils.py
├── templates/
├── static/
│   ├── css/
│   └── fonts/
├── .env
├── .gitignore
└── README.md
```

---

## 🛡️ Security Notes

- All secrets are stored in `.env` (and gitignored)  
- Passwords are hashed with Werkzeug  
- OTP verification uses Twilio + session tracking  
- Role-based access ensures restricted views/actions  

---

## 📈 Future Ideas

- Docker support  
- Multi-language plate format support  
- Plate scan history & analytics  
- Role-based permissions (more granular)  
- Export audit logs as CSV  

---

## 📜 License

MIT License

---

## 🧠 Inspiration

This started as a simple Flask project to test OCR... and quickly turned into a full-blown security-grade plate verification tool 🚗💡