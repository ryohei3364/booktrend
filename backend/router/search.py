from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from ..model.search import search
import json, os

search_router = APIRouter(prefix="/api/search", tags=["search"])

@search_router.get("/{lang}")
async def get_search(lang: str):
    supported_langs = ["en", "fr", "de", "it", "zh"]
    lang = lang if lang in supported_langs else "zh"
    file_path = f"backend/data/search_{lang}.json"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Language file not found")

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)
    
    return JSONResponse(content=data)

#/api/search?keyword=xxx
@search_router.get("")
async def search_by_keyword(keyword: str):
    result = search(keyword)
    return result