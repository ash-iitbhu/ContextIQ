from fastapi import APIRouter, Depends, HTTPException
from passlib.hash import bcrypt
from fastapi_jwt import JwtAccessBearer, JwtAuthorizationCredentials
from models import User
from services import AuthService

router = APIRouter()
jwt_bearer = JwtAccessBearer(secret_key="supersecret")
auth_service = AuthService()


@router.post("/register")
async def register(user: User):
    if auth_service.user_exists(user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    password_hash = bcrypt.hash(user.password)
    auth_service.insert_user(user.username, password_hash)
    return {"msg": "User registered successfully"}


@router.post("/login")
async def login(user: User):
    password_hash = auth_service.get_password_hash(user.username)
    if not password_hash or not bcrypt.verify(user.password, password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = jwt_bearer.create_access_token(subject={"username": user.username})
    return {"access_token": access_token}
