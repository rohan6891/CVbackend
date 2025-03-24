import os
from fastapi import APIRouter, HTTPException, Form
from database import users_collection
import bcrypt
import jwt
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

@router.post("/signup")
async def signup(email: str = Form(), password: str = Form()):
    if await users_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    await users_collection.insert_one({"email": email, "password": hashed_password})
    return {"message": "User registered"}

@router.post("/login")
async def login(email: str = Form(), password: str = Form()):
    db_user = await users_collection.find_one({"email": email})
    if not db_user or not bcrypt.checkpw(password.encode(), db_user["password"].encode()):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = jwt.encode({"email": email}, SECRET_KEY, algorithm=ALGORITHM)
    return {"token": token}
