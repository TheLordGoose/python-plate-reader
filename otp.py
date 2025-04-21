import random
import os
import sqlite3
from flask import session
from twilio.rest import Client
from datetime import datetime
from dotenv import load_dotenv

#Twilio setup
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_sms(phone_number, otp_code):
    message = client.messages.create(
        body=f'Your verification code is {otp_code}',
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    return message.sid
def get_admin_phone():
    db = sqlite3.connect("plates.db")
    cursor = db.cursor()
    cursor.execute("SELECT phone FROM otp_settings LIMIT 1")
    row = cursor.fetchone()
    db.close()
    return row[0] if row else None

def initiate_otp_flow():
    phone = get_admin_phone()
    if not phone:
        raise Exception("Admin OTP phone number not set!")
    
    otp = generate_otp()

    # Store OTP and time sent
    session["otp"] = otp
    session["otp_sent_at"] = datetime.utcnow().isoformat()

    client.messages.create(
        body=f"Your OTP is {otp}",
        from_=TWILIO_PHONE_NUMBER,
        to=phone
    )
