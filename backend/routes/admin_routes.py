# backend/routes/admin_routes.py

from flask import Blueprint, render_template, jsonify, current_app

# ✅ Define admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# 🧭 Admin Dashboard Page
@admin_bp.route('/')
def admin_dashboard():
    return render_template('admin_dashboard.html')


# 📋 Fetch All Users
@admin_bp.route('/users')
def fetch_users():
    try:
        users = current_app.mongo.db.users.find()
        user_list = [
            {**user, "_id": str(user["_id"])} for user in users
        ]

        return jsonify({
            "status": "success",
            "total": len(user_list),
            "users": user_list
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# 💉 Fetch All Health Data
@admin_bp.route('/health-data')
def fetch_health_data():
    try:
        data = current_app.mongo.db.health_data.find()
        health_list = [
            {**item, "_id": str(item["_id"])} for item in data
        ]

        return jsonify({
            "status": "success",
            "total": len(health_list),
            "data": health_list
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
