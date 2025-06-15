from fastapi import *
from fastapi.responses import JSONResponse
from ..model.search import search, hot_searches
import json, os

search_router = APIRouter(prefix="/api/search", tags=["search"])

#/api/search?keyword=xxx
@search_router.get("")
def search_by_keyword(request: Request, keyword: str):
    result = search(request, keyword)
    return result

@search_router.get("/hot")
def search_by_hot(request: Request):
    result = hot_searches(request)
    return result

