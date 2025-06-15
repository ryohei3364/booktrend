from fastapi.responses import JSONResponse
from fastapi import *
import os, json

def get_language_code(request: Request):
    user_lang_cookie = request.cookies.get("booktrend-lang")
    # user_lang_cookie = None  # 暫時不要使用 cookie
    print("從 Cookie 讀取的語言偏好:", user_lang_cookie)
    
    # 再拿 Accept-Language header 當 fallback
    accept_language = request.headers.get("accept-language", "")
    # print("Accept-Language 的語言偏好:", accept_language)

    # 決定使用語言優先順序，先用 Cookie 裡的，沒有再用 header
    if user_lang_cookie:
        language = [user_lang_cookie.lower()]
    else:
        language = [lang.strip().split(";")[0].lower() for lang in accept_language.split(",") if lang]
    print(language[0])
    return language[0]


def get_language_data(request: Request):
    primary_code = get_language_code(request)
    # 支援的語言對應檔案
    lang_map = {
        "de": "de.json",
        "tw": "zh.json",
        "zh": "zh.json",
        "en": "en.json",
        "fr": "fr.json",
    }

    filename = lang_map.get(primary_code)
    print(filename)
        
    if filename:
        json_path = os.path.join("frontend/static/data/language", filename)
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
              data = json.load(f)
            return JSONResponse({
              "language": primary_code,
              "content": data
            })
          
    # 如果全部都找不到，回傳預設英文語言檔
    fallback_path = "frontend/static/data/language/en.json"
    if os.path.exists(fallback_path):
        with open(fallback_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return JSONResponse({
            "language": 'en',
            "content": data
        })

    # 如果預設語言也不存在
    raise HTTPException(status_code=404, detail="找不到任何語言檔")

