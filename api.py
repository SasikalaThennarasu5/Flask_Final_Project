from flask import Blueprint, jsonify, request
from models import db, User

api = Blueprint("api", __name__)

# Get all users
@api.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "username": u.username, "email": u.email} for u in users])

# Create user
@api.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Missing fields"}), 400
    
    user = User(username=data["username"], email=data["email"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201
