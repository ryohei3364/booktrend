from fastapi import Request, APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os, json

language_router = APIRouter(prefix="/api/language", tags=["language"])

@language_router.get("")
async def get_language(request: Request):
    accept_language = request.headers.get("accept-language").split('-')[0] or request.headers.get("accept-language")
    print("收到的語言偏好:", accept_language)
    
    # 解析 accept-language，例如 "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    languages = [lang.split(";")[0].lower() for lang in accept_language.split(",")]

    # 支援的語言對應檔案
    lang_map = {
        "de": "de.json",
        "tw": "zh.json",
        "zh": "zh.json",
        "en": "en.json",
    }

    # 對應 JSON 資料夾路徑
    for lang_code in languages:
        filename = lang_map.get(lang_code)
        print(filename)
        if filename:
          json_path = os.path.join("frontend/static/data/language", filename)
          if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
              data = json.load(f)
            return JSONResponse(content={
              "message": f"載入語言檔: {lang_code}",
              "content": data
            })
          
    # 如果全部都找不到，回傳預設英文語言檔
    fallback_path = "frontend/static/data/language/en.json"
    if os.path.exists(fallback_path):
        with open(fallback_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return JSONResponse(content={
            "message": f"未找到符合的語言，預設載入英文",
            "content": data
        })

    # 如果預設語言也不存在
    raise HTTPException(status_code=404, detail="找不到任何語言檔")