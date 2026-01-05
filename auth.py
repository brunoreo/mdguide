
from flask import Blueprint, request, jsonify, current_app
from flask_mail import Message
from flask_mail import Mail
from db import users, resets
import bcrypt
import re
import secrets
from datetime import datetime, timedelta

auth_bp = Blueprint("auth", __name__)

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_strong_password(password):
    return len(password) >= 6 and any(c.isdigit() for c in password)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email", "").lower().strip()
    password = data.get("password", "")

    if not is_valid_email(email):
        return jsonify({"success": False, "message": "Invalid email format"}), 400
    
    if not is_strong_password(password):
        return jsonify({"success": False, "message": "Password too weak"}), 400

    if users.find_one({"email": email}):
        return jsonify({"success": False, "message": "Email already registered"}), 400

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    
    # 1. Create User (Unverified)
    users.insert_one({
        "email": email,
        "password": hashed_pw,
        "verified": False,
        "created_at": datetime.utcnow()
    })

    # 2. Generate 6-digit OTP
    otp_code = str(secrets.randbelow(1000000)).zfill(6)
    resets.update_one(
        {"email": email},
        {"$set": {"code": otp_code, "expireAt": datetime.utcnow() + timedelta(minutes=10)}},
        upsert=True
    )




    # 3. SEND REAL EMAIL
    try:
        
        msg = Message("Verify Your MediGuide Account", recipients= [email])
        msg.body = f"Hello! Your official verification code is: {otp_code}. It expires in 10 minutes."
        
        #current_app.mail.send(msg)
        mail = current_app.extensions.get('mail')
        if mail:
            mail.send(msg)
        else:
            print("Mail extension not found!")
    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to send email: {str(e)}"}), 500

    return jsonify({"success": True, "message": "Verification code sent to your real email"}), 201

@auth_bp.route("/verify-email", methods=["POST"])
def verify_email():
    data = request.json
    email = data.get("email", "").lower().strip()
    user_code = data.get("code", "")

    record = resets.find_one({"email": email, "code": user_code})
    
    if record and record["expireAt"] > datetime.utcnow():
        users.update_one({"email": email}, {"$set": {"verified": True}})
        resets.delete_one({"email": email})
        return jsonify({"success": True, "message": "Email verified successfully!"}), 200
    
    return jsonify({"success": False, "message": "Invalid or expired code"}), 400

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email", "").lower().strip()
    password = data.get("password", "")

    user = users.find_one({"email": email})
    if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        if not user.get("verified", False):
            return jsonify({"success": False, "message": "Please verify your email first"}), 403
            
        return jsonify({
            "success": True,
            "user_id": str(user["_id"]),
            "email": user["email"]
        }), 200

    return jsonify({"success": False, "message": "Invalid email or password"}), 401

