

# from flask import Blueprint, request, jsonify, current_app
# import requests
# import bcrypt
# import re
# import secrets
# import os
# from datetime import datetime, timedelta
# from db import users, resets

# auth_bp = Blueprint("auth", __name__)

# def is_valid_email(email):
#     return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# def is_strong_password(password):
#     return len(password) >= 6 and any(c.isdigit() for c in password)

# @auth_bp.route("/register", methods=["POST"])
# def register():
#     data = request.json
#     email = data.get("email", "").lower().strip()
#     password = data.get("password", "")

#     if not is_valid_email(email):
#         return jsonify({"success": False, "message": "Invalid email format"}), 400
    
#     if not is_strong_password(password):
#         return jsonify({"success": False, "message": "Password too weak"}), 400

#     if users.find_one({"email": email}):
#         return jsonify({"success": False, "message": "Email already registered"}), 400

#     hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    
#     # 1. Create User (Unverified)
#     users.insert_one({
#         "email": email,
#         "password": hashed_pw,
#         "verified": False,
#         "created_at": datetime.utcnow()
#     })

#     # 2. Generate 6-digit OTP
#     otp_code = str(secrets.randbelow(1000000)).zfill(6)
#     resets.update_one(
#         {"email": email},
#         {"$set": {"code": otp_code, "expireAt": datetime.utcnow() + timedelta(minutes=10)}},
#         upsert=True
#     )

#     # 3. SEND EMAIL VIA BREVO API (Bypasses Render SMTP Block)
#     try:
#         api_key = current_app.config.get('BREVO_API_KEY')
#         sender_email = current_app.config.get('MAIL_DEFAULT_SENDER')
        
#         if not api_key:
#             raise Exception("BREVO_API_KEY is not set in environment variables")

#         url = "https://api.brevo.com/v3/smtp/email"
#         payload = {
#             "sender": {"email": sender_email, "name": "MediGuide"},
#             "to": [{"email": email}],
#             "subject": "Verify Your MediGuide Account",
#             "htmlContent": f"""
#                 <html>
#                     <body>
#                         <h2>Welcome to MediGuide!</h2>
#                         <p>Your official verification code is: <strong>{otp_code}</strong></p>
#                         <p>This code expires in 10 minutes.</p>
#                     </body>
#                 </html>
#             """
#         }
#         headers = {
#             "accept": "application/json",
#             "content-type": "application/json",
#             "api-key": api_key
#         }

#         response = requests.post(url, json=payload, headers=headers)
        
#         if response.status_code not in [200, 201]:
#             print(f"Brevo Error: {response.text}")
#             raise Exception("Email provider refused the request")

#     except Exception as e:
#         # We still return 201 because the user was created, 
#         # but we notify them about the email failure
#         return jsonify({"success": False, "message": f"User created but email failed: {str(e)}"}), 500

#     return jsonify({"success": True, "message": "Verification code sent to your email"}), 201

# @auth_bp.route("/verify-email", methods=["POST"])
# def verify_email():
#     data = request.json
#     email = data.get("email", "").lower().strip()
#     user_code = data.get("code", "")

#     record = resets.find_one({"email": email, "code": user_code})
    
#     if record and record["expireAt"] > datetime.utcnow():
#         users.update_one({"email": email}, {"$set": {"verified": True}})
#         resets.delete_one({"email": email})
#         return jsonify({"success": True, "message": "Email verified successfully!"}), 200
    
#     return jsonify({"success": False, "message": "Invalid or expired code"}), 400

# @auth_bp.route("/login", methods=["POST"])
# def login():
#     data = request.json
#     email = data.get("email", "").lower().strip()
#     password = data.get("password", "")

#     user = users.find_one({"email": email})
#     if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
#         if not user.get("verified", False):
#             return jsonify({"success": False, "message": "Please verify your email first"}), 403
            
#         return jsonify({
#             "success": True,
#             "user_id": str(user["_id"]),
#             "email": user["email"]
#         }), 200

#     return jsonify({"success": False, "message": "Invalid email or password"}), 401



from flask import Blueprint, request, jsonify, current_app
import requests
import bcrypt
import secrets
from datetime import datetime, timedelta
from db import users, resets

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email", "").lower().strip()
    password = data.get("password", "")
    # New: Capture role from request
    role = data.get("role", "patient") 

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password required"}), 400

    if users.find_one({"email": email}):
        return jsonify({"success": False, "message": "Email already registered"}), 400

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    
    # 1. Create User with Role
    users.insert_one({
        "email": email,
        "password": hashed_pw,
        "role": role, # "patient" or "doctor"
        "verified": False,
        "created_at": datetime.utcnow()
    })

    # 2. Generate OTP
    otp_code = str(secrets.randbelow(1000000)).zfill(6)
    resets.update_one(
        {"email": email},
        {"$set": {"code": otp_code, "expireAt": datetime.utcnow() + timedelta(minutes=10)}},
        upsert=True
    )

    # 3. Send Email (Brevo)
    try:
        api_key = current_app.config.get('BREVO_API_KEY')
        sender_email = current_app.config.get('MAIL_DEFAULT_SENDER')
        
        url = "https://api.brevo.com/v3/smtp/email"
        payload = {
            "sender": {"email": sender_email, "name": "MediGuide"},
            "to": [{"email": email}],
            "subject": f"Verify your {role.capitalize()} Account",
            "htmlContent": f"<html><body><p>Your code is: <strong>{otp_code}</strong></p></body></html>"
        }
        headers = {"accept": "application/json", "content-type": "application/json", "api-key": api_key}
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        return jsonify({"success": False, "message": f"User created but email failed: {str(e)}"}), 500

    return jsonify({"success": True, "message": "Verification code sent"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email", "").lower().strip()
    password = data.get("password", "")

    user = users.find_one({"email": email})
    if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        if not user.get("verified", False):
            return jsonify({"success": False, "message": "Please verify your email"}), 403
            
        return jsonify({
            "success": True,
            "user_id": str(user["_id"]),
            "email": user["email"],
            "role": user.get("role", "patient") # Returns role for UI routing
        }), 200

    return jsonify({"success": False, "message": "Invalid credentials"}), 401