from fastapi import APIRouter, HTTPException, Request
from models.user_model import RegisterForm, LoginForm
from logic.auth_service import register_user, login_user, verify_password, create_access_token
from app_utils.jwt import decode_token
from app_utils.db import get_cursor  # ✅ 用安全版本

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register")
def register(form: RegisterForm):
    result = register_user(form.name, form.email, form.password)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"message": "註冊成功"}

@router.post("/login")
def login(form: LoginForm):
    with get_cursor() as cursor:  # ✅ 使用 context manager
        cursor.execute("SELECT * FROM users WHERE email = %s", (form.email,))
        user = cursor.fetchone()

    if not user or not verify_password(form.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="登入失敗")

    token = create_access_token({
        "sub": str(user["id"]),
        "email": user["email"],
        "name": user["name"]
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "name": user["name"]
    }

def get_current_user(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登入")
    token = auth.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=403, detail="無效的 token")
    return payload
