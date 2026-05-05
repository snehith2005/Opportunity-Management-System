from flask import Blueprint, request, jsonify
from models import db, Admin, Opportunity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import secrets
import re

main = Blueprint("main", __name__)

ALLOWED_CATEGORIES = ["technology", "business", "design", "marketing", "data science", "other"]

# ---------- SIGNUP ----------
@main.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()
        print("DATA:", data)

        if not all([data.get("full_name"), data.get("email"), data.get("password"), data.get("confirm_password")]):
            return jsonify({"error": "All fields required"}), 400

        if not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
            return jsonify({"error": "Invalid email"}), 400

        if data["password"] != data["confirm_password"]:
            return jsonify({"error": "Passwords do not match"}), 400

        if len(data["password"]) < 8:
            return jsonify({"error": "Password too short"}), 400

        if Admin.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "Email already exists"}), 400

        user = Admin(
            full_name=data["full_name"],
            email=data["email"],
            password_hash=generate_password_hash(data["password"])
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "Signup successful"})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

# ---------- LOGIN ----------
@main.route("/login", methods=["POST"])

def login():
    data = request.get_json()

    user = Admin.query.filter_by(email=data.get("email")).first()

    if not user or not check_password_hash(user.password_hash, data.get("password")):
        return jsonify({"error": "Invalid email or password"}), 401

    # ✅ THIS IS WHERE IT GOES
    login_user(user, remember=True)

    return jsonify({"message": "Login successful"})

# ---------- FORGOT PASSWORD ----------
@main.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()

    user = Admin.query.filter_by(email=data.get("email")).first()

    if user:
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()

        print(f"RESET LINK: http://127.0.0.1:5000/reset-password/{token}")

    return jsonify({"message": "If email exists, reset link sent"})


@main.route("/reset-password/<token>", methods=["GET","POST"])
def reset_password(token):
    admin = Admin.query.filter_by(reset_token=token).first()
    if not admin:
        return "Invalid or expired reset link"
    if request.method == "POST":
        new_password = request.form.get("password")

        print("NEW PASSWORD:", new_password) 
        print("USER:", admin.email)          

        if not new_password:
            return "Password required"

        admin.password_hash = generate_password_hash(new_password)
        admin.reset_token = None

        db.session.commit()

        print("UPDATED SUCCESSFULLY")  

        return "Password reset successful You can login now."

    return """
    <h2>Reset Password</h2>
    <form method="POST">
        <input type="password" name="password" placeholder="New Password" required />
        <button type="submit">Reset Password</button>
    </form>
    """


# ---------- GET ALL ----------
@main.route("/opportunities", methods=["GET"])
@login_required
def get_all():
    ops = Opportunity.query.filter_by(admin_id=current_user.id).all()

    return jsonify([{
        "id": o.id,
        "title": o.title,
        "duration": o.duration,
        "start_date": o.start_date,
        "description": o.description,
        "skills": o.skills,
        "category": o.category,
        "future_opportunities": o.future_opportunities,   
        "applicants": getattr(o, "applicants", 0)         
    } for o in ops])


# ---------- ADD ----------
@main.route("/opportunities", methods=["POST"])
@login_required
def add():
    try:
        data = request.get_json() or {}
        print("DATA RECEIVED:", data)

        required = ["title","duration","start_date","description","skills","category","future_opportunities"]

        if not all(data.get(f) for f in required):
            return jsonify({"error": "All fields required"}), 400

        if data["category"].lower() not in [c.lower() for c in ALLOWED_CATEGORIES]:
            return jsonify({"error": "Invalid category"}), 400

        from datetime import datetime
        data["start_date"] = datetime.strptime(data["start_date"], "%Y-%m-%d")

        op = Opportunity(**data, admin_id=current_user.id)

        db.session.add(op)
        db.session.commit()

        return jsonify({"message": "Created"})

    except Exception as e:
        print("ERROR:", str(e))  
        return jsonify({"error": str(e)}), 500

# ---------- UPDATE ----------

@main.route("/opportunities/<int:id>", methods=["PUT"])
@login_required
def update(id):
    op = Opportunity.query.get_or_404(id)

    if op.admin_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    print("DATA:", data)  

    if not data:
        return jsonify({"error": "No data received"}), 400

    # Safe update
    if "title" in data:
        op.title = data["title"]
    if "description" in data:
        op.description = data["description"]
    if "duration" in data:
        op.duration = data["duration"]
    if "skills" in data:
        op.skills = data["skills"]
    if "category" in data:
        op.category = data["category"]
    if "start_date" in data:
        op.start_date = data["start_date"]

    db.session.commit()

    print("UPDATED:", op.title)  

    return jsonify({"message": "Updated successfully"})


# ---------- DELETE ----------
@main.route("/opportunities/<int:id>", methods=["DELETE"])
@login_required
def delete(id):
    op = Opportunity.query.get_or_404(id)

    if op.admin_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(op)
    db.session.commit()

    return jsonify({"message": "Deleted"})


@main.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"})