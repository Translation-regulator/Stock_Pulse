from passlib.context import CryptContext # type: ignore
from app_utils.jwt import create_access_token
from app_utils.db import get_connection

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def register_user(name: str, email: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        return {"error": "Email 已註冊"}
    hashed = hash_password(password)
    cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
        (name, email, hashed)
    )
    conn.commit()
    return {"success": True}

def login_user(email: str, password: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user or not verify_password(password, user["password_hash"]):
        return {"error": "登入失敗"}
    token = create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

