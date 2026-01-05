
from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
from auth import auth_bp
# Import other blueprints
from medications import meds_bp
from history import history_bp
# from transcription import trans_bp

app = Flask(__name__)
CORS(app, supports_credentials=True)

# --- REAL EMAIL CONFIGURATION ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465#587
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'myappmedi001@gmail.com'  # Your real Gmail
app.config['MAIL_PASSWORD'] = 'rdefxcmoyipwgiji'  # Your 16-digit App Password
app.config['MAIL_DEFAULT_SENDER'] = 'myappmedi001@gmail.com'#'MediGuide Admin'

# Initialize Mail
mail = Mail(app)

# Attach mail to the app so blueprints can access it via 'current_app'
app.mail = mail 

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(meds_bp, url_prefix="/api")
app.register_blueprint(history_bp, url_prefix="/api")
# app.register_blueprint(trans_bp, url_prefix="/api")

@app.route("/")
def index():
    return {"message": "MediGuide API running"}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)