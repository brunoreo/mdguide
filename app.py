

import os
from flask import Flask
from flask_cors import CORS
from auth import auth_bp
from medications import meds_bp
from history import history_bp

app = Flask(__name__)
CORS(app, supports_credentials=True)

# --- CONFIGURATION VIA ENVIRONMENT VARIABLES ---
# We use the Brevo API Key instead of SMTP settings
app.config['BREVO_API_KEY'] = os.environ.get('BREVO_API_KEY')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'myappmedi001@gmail.com')

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(meds_bp, url_prefix="/api")
app.register_blueprint(history_bp, url_prefix="/api")

@app.route("/")
def index():
    return {"status": "online", "message": "MediGuide API is running"}

if __name__ == "__main__":
    # Render uses the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)