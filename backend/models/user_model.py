def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "name": user["name"],
        "hashed_password": user["hashed_password"]
    }
