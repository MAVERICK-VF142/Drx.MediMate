from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import mimetypes

app = FastAPI()

# Allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to specific domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "pharmacist_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Dummy DB
pharmacist_db = {}

@app.post("/upload_certificate/")
async def upload_certificate(name: str = Form(...), file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.endswith(".pdf") or file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # Validate file size (max 2MB)
    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 2MB.")

    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"{name}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(contents)

    # Add to mock DB
    pharmacist_db[name] = {"file": file_path, "verified": False}

    return JSONResponse(content={"message": "File uploaded for review."})

@app.get("/verify_pharmacist/{name}")
def verify_pharmacist(name: str):
    if name not in pharmacist_db:
        raise HTTPException(status_code=404, detail="Pharmacist not found.")
    
    pharmacist_db[name]["verified"] = True
    return {"message": f"{name} is now verified ✅"}

@app.get("/check_verification/{name}")
def check_verification(name: str):
    status = pharmacist_db.get(name)
    if not status:
        return {"verified": False}
    return {"verified": status["verified"]}
