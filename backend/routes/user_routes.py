from fastapi import APIRouter, HTTPException
from backend.config.db import db
from backend.models.user_model import user_helper
from backend.utils.auth import hash_password, verify_password


router = APIRouter()

@router.post("/register")
def register_user(user: dict):
    user["hashed_password"] = hash_password(user["password"])
    del user["password"]
    result = db.users.insert_one(user)
    return {"id": str(result.inserted_id)}

@router.post("/login")
def login_user(credentials: dict):
    user = db.users.find_one({"email": credentials["email"]})
    if user and verify_password(credentials["password"], user["hashed_password"]):
        return user_helper(user)
    raise HTTPException(status_code=401, detail="Invalid credentials")
