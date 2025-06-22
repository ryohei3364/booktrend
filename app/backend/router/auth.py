from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse, RedirectResponse
# from ..model.language import get_language_code, get_language_data
from ..model.auth import Auth
from dotenv import load_dotenv
import os, urllib.parse, requests
from ..database import db_pool
    
# 本機測試: http://localhost:8080/api/auth/google/callback
# 部署測試: https://booktrend.online/api/auth/google/callback

load_dotenv()

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "https://booktrend.online/api/auth/google/callback"
REDIRECT_URI_test = "http://localhost:8080/api/auth/google/callback"


# 產生 Google OAuth 授權 URL 的路由
@auth_router.get("/google")
def get_google_oauth_url():
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI_test,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent select_account"
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    print(url)
    return JSONResponse(content={"url": url})


# Google 授權後回傳 code 的處理路由
@auth_router.get("/google/callback")
def google_oauth_callback(request: Request, code: str):
    code = request.query_params.get("code")
    print("收到 Google code:", code)
    if not code:
        return JSONResponse({"error": "No code provided"}, status_code=400)

    # Step 1: 用 code 換 access_token
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI_test,
        "grant_type": "authorization_code",
    }

    token_response = requests.post(token_url, data=data)
    token_json = token_response.json()
    access_token = token_json.get("access_token")
    print(access_token)
    
    # Step 2: 用 access_token 拿使用者資訊
    userinfo_response = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    userinfo = userinfo_response.json()
    print("👤 User Info:", userinfo)

    # Step 3: 寫入資料庫
    userinfo = Auth.insert_user_data_google(userinfo)
    return userinfo


# 前端 email 回傳 處理路由
@auth_router.post("/login")
async def login(request: Request):
    try:
        # 從前端取得 JSON 資料
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return JSONResponse(status_code=400, content={"error": "缺少必要欄位"})
        
        user = Auth.get_user_by_email(email)
        if not user:
            # 尚未註冊，前端收到 404 可跳轉註冊頁
            return JSONResponse(status_code=404, content={"error": "找不到使用者，請註冊"})

        result = Auth.check_user_credentials(email, password)
        if not result:
            # 帳號存在但密碼錯誤
            return JSONResponse(status_code=401, content={"error": "帳號或密碼錯誤"})

        token = Auth.encoded_jwt({
            "id": result["id"],
            "name": result["name"],
            "email": result["email"],
            "picture": result["picture"]
        })
        return JSONResponse(content={"token": token, "user": result})
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
        

# 前端 email 回傳 處理路由
@auth_router.post("/register")
async def register(request: Request):
    try:
        # 從前端取得 JSON 資料
        data = await request.json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        
        if not name or not email or not password:
            return JSONResponse(status_code=400, content={"error": "缺少必要欄位"})
        
        # 檢查是否已註冊
        existing_user = Auth.get_user_by_email(email)
        if existing_user:
            return JSONResponse(status_code=400, content={"error": "此 Email 已註冊"})

        # 加密後寫入
        hashed_password = Auth.hash_password(password)
        userinfo = {
            "name": name,
            "email": email,
            "password": hashed_password
        }
        # 寫入資料庫並取得使用者
        user = Auth.insert_user_data_email(userinfo)
        # 建立 JWT Token
        token = Auth.encoded_jwt({
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "picture": user.get("picture", None)
        })
        print('token:', token, 'user:', user)
        return JSONResponse(content={"token": token, "user": user})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
    
@auth_router.get("/profile")
def get_user_profile(request: Request):
    user = Auth.get_current_user(request)
    return user
