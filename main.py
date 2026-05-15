from fastapi import (
    FastAPI,
    HTTPException,
    Header,
    UploadFile,
    File,
    Form
)
import os
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from passlib.context import CryptContext

from database import users, videos_collection
from auth import create_token, verify_token
from video_generator import generate_video

import os
import shutil
import hashlib


# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI(
    title="AI Image-to-Video Generator API"
)


# ==========================================
# CREATE DIRECTORIES
# ==========================================

os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)


# ==========================================
# STATIC FILES
# ==========================================

app.mount(
    "/outputs",
    StaticFiles(directory="outputs"),
    name="outputs"
)


# ==========================================
# PASSWORD HASHING SETUP
# ==========================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    bcrypt__default_rounds=12
)


# ==========================================
# REQUEST MODELS
# ==========================================

class SignupModel(BaseModel):
    name: str
    username: str
    email: str
    password: str


class LoginModel(BaseModel):
    email_or_username: str
    password: str


class ForgotPasswordModel(BaseModel):
    email: str


class ResetPasswordModel(BaseModel):
    email: str
    new_password: str


# ==========================================
# SAFE PASSWORD FUNCTIONS (FIXED)
# ==========================================

def normalize_password(password: str) -> str:
    """
    Prevent bcrypt 72-byte limitation crash
    """
    if len(password.encode("utf-8")) > 72:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()
    return password


def hash_password(password: str):
    password = normalize_password(password)
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    password = normalize_password(password)
    return pwd_context.verify(password, hashed_password)


# ==========================================
# SIGNUP
# ==========================================

@app.post("/signup")
async def signup(user: SignupModel):

    existing_email = await users.find_one({"email": user.email})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    existing_username = await users.find_one({"username": user.username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = {
        "name": user.name,
        "username": user.username,
        "email": user.email,
        "password": hash_password(user.password)
    }

    await users.insert_one(new_user)

    return {
        "status": "success",
        "message": "User created successfully"
    }


# ==========================================
# LOGIN
# ==========================================

@app.post("/login")
async def login(user: LoginModel):

    db_user = await users.find_one({
        "$or": [
            {"email": user.email_or_username},
            {"username": user.email_or_username}
        ]
    })

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_token({"email": db_user["email"]})

    return {
        "status": "success",
        "access_token": token,
        "user": {
            "name": db_user["name"],
            "username": db_user["username"],
            "email": db_user["email"]
        }
    }


# ==========================================
# FORGOT PASSWORD
# ==========================================

@app.post("/forgot-password")
async def forgot_password(data: ForgotPasswordModel):

    user = await users.find_one({"email": data.email})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "status": "success",
        "message": "Password reset request successful"
    }


# ==========================================
# RESET PASSWORD
# ==========================================

@app.post("/reset-password")
async def reset_password(data: ResetPasswordModel):

    user = await users.find_one({"email": data.email})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await users.update_one(
        {"email": data.email},
        {"$set": {"password": hash_password(data.new_password)}}
    )

    return {
        "status": "success",
        "message": "Password reset successful"
    }


# ==========================================
# GET PROFILE
# ==========================================

@app.get("/profile")
async def get_profile(authorization: str = Header(None)):

    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization token missing")

    token = authorization.replace("Bearer ", "")
    decoded = verify_token(token)

    if not decoded:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await users.find_one({"email": decoded["email"]})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "status": "success",
        "user": {
            "name": user["name"],
            "username": user["username"],
            "email": user["email"]
        }
    }


# ==========================================
# GENERATE VIDEO
# ==========================================

@app.post("/generate-video")
async def generate_video_endpoint(
    file: UploadFile = File(...),
    motion: str = Form("zoom"),
    frames: int = Form(8),
    authorization: str = Header(None)
):
    # =========================
    # AUTH CHECK
    # =========================
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization token missing")

    token = authorization.replace("Bearer ", "").strip()
    decoded = verify_token(token)

    if not decoded:
        raise HTTPException(status_code=401, detail="Invalid token")

    # =========================
    # CREATE UPLOAD DIR
    # =========================
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # =========================
    # SAVE IMAGE SAFELY
    # =========================
    file_ext = file.filename.split(".")[-1]

    safe_email = decoded["email"].replace("@", "_").replace(".", "_")

    image_path = f"uploads/{safe_email}_upload.{file_ext}"

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # =========================
    # GENERATE VIDEO
    # (IMPORTANT: must match your function signature)
    # =========================
    try:
        output_video = generate_video(
            image_path=image_path,
            motion=motion,
            frames=frames
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Video generation failed: {str(e)}"
        )

    # =========================
    # SAVE HISTORY
    # =========================
    await videos_collection.insert_one({
        "email": decoded["email"],
        "image_path": image_path,
        "video_path": output_video,
        "motion": motion,
        "frames": frames
    })

    # =========================
    # RESPONSE
    # =========================
    return {
        "status": "success",
        "motion": motion,
        "frames": frames,
        "video_url": output_video
    }

# ==========================================
# GET HISTORY
# ==========================================

@app.get("/history")
async def get_history(authorization: str = Header(None)):

    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization token missing")

    token = authorization.replace("Bearer ", "")
    decoded = verify_token(token)

    if not decoded:
        raise HTTPException(status_code=401, detail="Invalid token")

    history = await videos_collection.find(
        {"email": decoded["email"]}
    ).to_list(100)

    return {
        "status": "success",
        "videos": [
            {
                "motion": item["motion"],
                "frames": item["frames"],
                "image_path": item["image_path"],
                "video_path": item["video_path"]
            }
            for item in history
        ]
    }


# ==========================================
# DELETE VIDEO
# ==========================================

@app.delete("/delete-video/{video_name}")
async def delete_video(video_name: str, authorization: str = Header(None)):

    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization token missing")

    token = authorization.replace("Bearer ", "")
    decoded = verify_token(token)

    if not decoded:
        raise HTTPException(status_code=401, detail="Invalid token")

    video_path = f"outputs/{video_name}"

    if os.path.exists(video_path):
        os.remove(video_path)

    await videos_collection.delete_one({
        "email": decoded["email"],
        "video_path": video_path
    })

    return {
        "status": "success",
        "message": "Video deleted successfully"
    }


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/")
async def home():
    return {
        "status": "running",
        "message": "AI Video Generator Backend Running Successfully"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))