from fastapi.responses import JSONResponse
from fastapi import *
from functools import lru_cache
import os, json

# 支援的語言對應檔案
LANG_MAP = {
    "de": "de.json",
    "zh-tw": "zh.json",
    "en-us": "en.json",
    "fr": "fr.json",
}
    
@lru_cache(maxsize=10)
def load_language_json(filename: str):
    json_path = os.path.join("frontend/static/data/language", filename)
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def get_language_code(request: Request):
    user_lang_cookie = request.cookies.get("booktrend-lang")
    # user_lang_cookie = None  # 暫時不要使用 cookie
    print("從 Cookie 讀取的語言偏好:", user_lang_cookie)
    
    # 再拿 Accept-Language header 當 fallback
    accept_language = request.headers.get("accept-language", "")
    # print("Accept-Language 的語言偏好:", accept_language)

    # # 決定使用語言優先順序，先用 Cookie 裡的，沒有再用 header
    # if user_lang_cookie:
    #     language = [user_lang_cookie.lower()]
    # else:
    #     language = [lang.strip().split(";").lower() for lang in accept_language.split(",") if lang]
    # print(language[0])
    # return language[0]
    if user_lang_cookie:
        return user_lang_cookie.lower()

    for lang in accept_language.split(","):
        primary = lang.strip().split(";")[0].lower()
        if primary in LANG_MAP:
            return primary
    return "en-us"


def get_language_data(request: Request):
    primary_code = get_language_code(request)
    print("primary_code:", primary_code)

    filename = LANG_MAP.get(primary_code)
    print(filename)
    
    if filename:
        data = load_language_json(filename)
        if data:
            return JSONResponse({
                "language": primary_code,
                "content": data
            })

    # fallback 英文
    data = load_language_json("en.json")
    if data:
        return JSONResponse({
            "language": "en",
            "content": data
        })
    # if filename:
    #     json_path = os.path.join("frontend/static/data/language", filename)
    #     if os.path.exists(json_path):
    #         with open(json_path, "r", encoding="utf-8") as f:
    #           data = json.load(f)
    #         return JSONResponse({
    #           "language": primary_code,
    #           "content": data
    #         })
          
    # # 如果全部都找不到，回傳預設英文語言檔
    # fallback_path = "frontend/static/data/language/en.json"
    # if os.path.exists(fallback_path):
    #     with open(fallback_path, "r", encoding="utf-8") as f:
    #         data = json.load(f)
    #     return JSONResponse({
    #         "language": 'en',
    #         "content": data
    #     })

    # 如果預設語言也不存在
    raise HTTPException(status_code=404, detail="找不到任何語言檔")

