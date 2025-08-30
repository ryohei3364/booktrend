from fastapi import Request, APIRouter, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
# from ..model.language import get_language_code, get_language_data
from ..model.auth import Auth
from dotenv import load_dotenv
import os, urllib.parse, requests, logging
from ..database import db_pool
from pydantic import BaseModel, EmailStr, Field

# 定義 request body schema
# 前端登入資料
class LoginSchema(BaseModel):
    email: str
    password: str
    # email: EmailStr = Field(..., description="使用者 Email")
    # password: str = Field(..., min_length=4, description="使用者密碼，至少 4 位")

# 前端註冊資料
class RegisterSchema(LoginSchema):
    name: str
    # name: str = Field(..., min_length=2, description="使用者姓名，至少 2 個字")
    
# 本機測試: http://localhost:8080/api/auth/google/callback
# 部署測試: https://booktrend.online/api/auth/google/callback

load_dotenv()

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "https://booktrend.online/api/auth/google/callback"
REDIRECT_URI_test = "http://localhost:8000/api/auth/google/callback"


# 產生 Google 授權 URL
@auth_router.get("/google")
def get_google_oauth_url():
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent select_account"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    print(url)
    return JSONResponse(content={"url": url})


# 拿到 code 並成功換取 access_token、id_token
@auth_router.get("/google/callback")
def google_oauth_callback(code: str):
    try:
        print("收到 Google code:", code)
        if not code:
            return JSONResponse({"error": "No code provided"}, status_code=400)

        # Step 1: 用 code 換 token
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        token_response = requests.post(token_url, data=data)
        # print("Token response:", token_response.text)

        if token_response.status_code != 200:
            return JSONResponse(status_code=500, content={"error": "取得 token 失敗", "detail": token_response.text})

        token_json = token_response.json()
        id_token_str = token_json.get("id_token")

        # Step 2: 驗證 id_token
        user_info = Auth.verify_google_id_token(id_token_str, GOOGLE_CLIENT_ID)
        if not user_info:
            return JSONResponse({"error": "id_token 驗證失敗"}, status_code=400)

        # Step 3: 查詢或建立會員
        db_user = Auth.get_user_by_email(user_info["email"])
        if not db_user:
            db_user = Auth.insert_user_data_google(user_info)

        # Step 4: 用 DB 資料簽發 JWT
        jwt_token = Auth.encoded_jwt(db_user)
        # return JSONResponse({"ok": True, "token": jwt_token, "user": db_user})   
        
        # Step 5: 透過 RedirectResponse 導回前端頁面，JWT 放在 query string
        frontend_redirect = "http://localhost:8000"  # 或 production URL
        redirect_url_test = f"{frontend_redirect}?token={jwt_token}"
        return RedirectResponse(redirect_url_test) 

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "callback 錯誤", "detail": str(e)})
    

# 前端 email 回傳 處理路由
@auth_router.post("/login")
async def login(data: LoginSchema):
    try:
        user = Auth.get_user_by_email(data.email)
        if not user:
            # Email 不存在
            raise HTTPException(status_code=404, detail="找不到使用者，請註冊")

        password = Auth.check_password(data.password, user["password"])
        if not password:
            # 密碼錯誤
            raise HTTPException(status_code=401, detail="帳號或密碼錯誤")

        # token = Auth.encoded_jwt(user)
        token = Auth.encoded_jwt(Auth.user_payload(user))
        return {"token": token, "user": user}
    
    except Exception as e:
        # 記錄 log，方便除錯
        logging.error(f"Internal server error: {e}")
        # 回傳統一訊息給前端
        raise HTTPException(status_code=500, detail="伺服器內部錯誤")        


# 前端 email 回傳 處理路由
@auth_router.post("/register")
async def register(data: RegisterSchema):
    try:
        user = Auth.get_user_by_email(data.email)
        if user:
            return JSONResponse(status_code=400, content={"error": "此 Email 已註冊"})

        # 加密後寫入
        hashed_password = Auth.hash_password(data.password)
        userinfo = {
            "name": data.name,
            "email": data.email,
            "password": hashed_password
        }
        # 寫入資料庫並取得使用者
        insert_user = Auth.insert_user_data_email(userinfo)
        # 建立 JWT Token
        token = Auth.encoded_jwt({
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "picture": user.get("picture", None)
        })
        print('token:', token, 'user:', insert_user)
        return JSONResponse(content={"token": token, "user": insert_user})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    
@auth_router.get("/profile")
def get_user_profile(request: Request):
    user = Auth.get_current_user(request)
    return user
