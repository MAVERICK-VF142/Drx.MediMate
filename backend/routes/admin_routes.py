from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import datetime
import secrets
import uuid
import logging

from firebase_admin import firestore

# Firestore DB reference
db = firestore.client()

# Create Blueprint
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Utility to parse Firestore timestamps
def parse_firestore_timestamp(timestamp):
    if isinstance(timestamp, datetime.datetime):
        return timestamp
    if hasattr(timestamp, "to_datetime"):
        try:
            return timestamp.to_datetime()
        except Exception as e:
            logging.error(f"Failed to convert Firestore Timestamp to datetime: {e}")
            return None
    if isinstance(timestamp, str):
        try:
            return datetime.datetime.fromisoformat(timestamp)
        except (ValueError, TypeError):
            logging.error(f"Could not parse timestamp string: {timestamp}")
            return None
    logging.warning(f"Unhandled timestamp type: {type(timestamp)}")
    return None

# Auth decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("sisu"))
        if session.get("role") != "admin":
            return render_template("unauthorized.html", message="Admin access required"), 403
        return f(*args, **kwargs)
    return decorated_function

# Admin Dashboard
@admin_bp.route("/dashboard")
@admin_required
def admin_dashboard():
    return render_template("admin-dashboard.html")

# -------------------
# Admin Invitations
# -------------------

def generate_invitation_code():
    return secrets.token_urlsafe(16)

def create_admin_invitation(email, expiry_hours=48):
    invitation_id = str(uuid.uuid4())
    invitation_code = generate_invitation_code()

    current_time = datetime.datetime.now()
    expiry_time = current_time + datetime.timedelta(hours=expiry_hours)

    invitation_data = {
        "id": invitation_id,
        "email": email,
        "code": invitation_code,
        "created_at": current_time,
        "expires_at": expiry_time,
        "used": False,
    }

    db.collection("admin_invitations").document(invitation_code).set(invitation_data)
    return invitation_code

@admin_bp.route("/api/invitation", methods=["POST"])
@admin_required
def create_invitation():
    try:
        data = request.get_json()
        email = data.get("email")
        if not email:
            return jsonify({"success": False, "message": "Email is required"}), 400

        code = create_admin_invitation(email)
        return jsonify({
            "success": True,
            "invitation_code": code,
            "message": f"Invitation created for {email}"
        })
    except Exception as e:
        logging.error(f"Error creating invitation: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route("/api/verify-invitation", methods=["POST"])
def verify_invitation():
    try:
        data = request.get_json()
        code = data.get("code")
        email = data.get("email")

        if not code or not email:
            return jsonify({"success": False, "message": "Code and email are required"}), 400

        invitation_ref = db.collection("admin_invitations").document(code)
        transaction = db.transaction()

        @firestore.transactional
        def _verify_and_use(txn):
            snapshot = invitation_ref.get(transaction=txn)
            if not snapshot.exists:
                return False, "Invalid invitation code"

            invitation = snapshot.to_dict()

            if invitation["email"].lower() != email.lower():
                return False, "This invitation is not for this email address"

            if invitation.get("used"):
                return False, "Invitation already used"

            expires_at = parse_firestore_timestamp(invitation.get("expires_at"))
            if not expires_at or datetime.datetime.now() > expires_at:
                return False, "Invitation expired"

            txn.update(invitation_ref, {"used": True})
            return True, invitation

        success, result = _verify_and_use(transaction)
        if success:
            return jsonify({"success": True, "message": "Invitation code is valid"})
        else:
            return jsonify({"success": False, "message": result}), 400

    except Exception as e:
        logging.error(f"Error verifying invitation: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route("/api/invitations", methods=["GET"])
@admin_required
def list_invitations():
    try:
        invitations = db.collection("admin_invitations").stream()
        result = []

        for invite in invitations:
            data = invite.to_dict()
            for key in ["created_at", "expires_at"]:
                if isinstance(data.get(key), datetime.datetime):
                    data[key] = data[key].isoformat()
            result.append(data)

        return jsonify({"success": True, "invitations": result})
    except Exception as e:
        logging.error(f"Error fetching invitations: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500
