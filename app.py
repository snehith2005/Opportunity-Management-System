import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from flask import Flask, send_from_directory
from config import Config
from models import db, Admin
from routes import main
from flask_login import LoginManager
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)
app.config["SECRET_KEY"] = "supersecretkey"
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False   # True only for HTTPS

db.init_app(app)
with app.app_context():
    db.create_all()
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

app.register_blueprint(main)

# Serve frontend
@app.route("/")
def home():
    return send_from_directory("sky", "admin.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("sky", path)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # local only
    app.run(debug=True)