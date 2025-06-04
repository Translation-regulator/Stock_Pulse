import os
from datetime import datetime, timedelta
from jose import jwt, JWTError # type: ignore
from dotenv import load_dotenv
from fastapi import Request, HTTPException
from app_utils.db import get_connection

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# 建立 JWT Token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# 解碼 JWT Token
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# 從 request 取得目前登入的使用者資料
def get_current_user(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登入")

    token = auth.split(" ")[1]
    payload = decode_token(token)

    if not payload or "sub" not in payload:
        raise HTTPException(status_code=403, detail="無效的 token")

    # 用 id 查詢
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email FROM users WHERE id = %s", (payload["sub"],))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="使用者不存在")

    return user  # 回傳完整 user 資料
