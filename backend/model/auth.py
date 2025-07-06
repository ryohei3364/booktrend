from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse, RedirectResponse
from dotenv import load_dotenv
from ..database import db_pool
from datetime import datetime, timedelta, timezone
import jwt, os, bcrypt, random

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ALGORITHM = os.getenv("ALGORITHM")

class Auth:
  def get_current_user(request: Request):
    authorization = request.headers.get("Authorization")
    if not authorization or authorization == "Bearer null":
      return JSONResponse("請先登入網站", status_code=403)
    try:
      token = authorization.split("Bearer ")[1]
      print(token)
      decoded_token = jwt.decode(token, PRIVATE_KEY, ALGORITHM)
      print(decoded_token)
      return {"data": decoded_token}
    except jwt.ExpiredSignatureError:
      return JSONResponse("使用者登入憑證已過期")

  def get_user_id(user):
    if isinstance(user, JSONResponse):
      return user
    return user["data"]["id"]
    
  def hash_password(password):
    input_password = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(input_password, bcrypt.gensalt(rounds=4)) 
    # print('input_password', input_password)
    # print('hashed_password', hashed_password)
    # print('hashed_password.decode:', hashed_password.decode("utf-8"))
    return hashed_password.decode("utf-8")
  
  def check_password(password, hashed_password):
    if isinstance(hashed_password, str):
      hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)

  def encoded_jwt(result):
    exp_time = (datetime.now(tz=timezone.utc) + timedelta(days=7)).timestamp()
    payload = {
      "id": result['id'],
      "name": result['name'],
      "email": result['email'],
      "exp": int(exp_time)
    }
    return jwt.encode(payload, PRIVATE_KEY, ALGORITHM)

  def insert_user_data_google(userinfo: dict):
    name = userinfo.get("name")
    email = userinfo.get("email")
    google_id = userinfo.get("id")
    picture = userinfo.get("picture")
    print(name, email, google_id, picture)

    if not email or not google_id:
        raise ValueError("缺少必要欄位")
      
    query = """
    INSERT INTO members (name, email, google_id, picture, source)
    VALUES (%s, %s, %s, %s, %s)
    """
    return db_pool.insert_cursor(query, (name, email, google_id, picture, 'google'))

  def insert_user_data_email(userinfo: dict):
    name = userinfo.get("name")
    email = userinfo.get("email")
    password = userinfo.get("password")
    print(name, email, password)

    if not email or not password:
        raise ValueError("缺少必要欄位")
      
    insert_query = """
    INSERT INTO members (name, email, password, source)
    VALUES (%s, %s, %s, %s)
    """
    db_pool.insert_cursor(insert_query, (name, email, password, 'email'))
    # ✅ 插入後立刻撈出 user 資料
    return Auth.get_user_by_email(email)
  
  @staticmethod
  def get_user_by_email(email: str):
    query = "SELECT id, name, email, password, picture FROM members WHERE email = %s"
    result = db_pool.get_cursor(query, (email,), fetch=True)
    return result[0] if result else None

  @staticmethod
  def check_user_credentials(email: str, password: str):
    print(f'email:{email}, password:{password}')
    user = Auth.get_user_by_email(email)
    if not user:
      return None
    hashed_password = user["password"]
    print("hashed_password:", hashed_password)
    print("input password:", password)
    result = Auth.check_password(password, hashed_password)
    print("check_password result:", result)
    if result:
        return user
    else:
        return None

