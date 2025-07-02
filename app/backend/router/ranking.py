from fastapi import *
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ..model.ranking import get_ranking_data, get_ranking_list

ranking_router = APIRouter(prefix="/api/ranking", tags=["ranking"])

#/api/ranking?bookstore_id=xxx&chart_type=xxx
@ranking_router.get("")
def get_rankings(bookstore_id:int, chart_type: str):
    result = get_ranking_data(bookstore_id, chart_type)
    return result[:10]

#/api/ranking/list
@ranking_router.get("/list")
async def get_list(request: Request):
    result = get_ranking_list(request)
    if not result:
        return JSONResponse(content={"error": "No ranking data found"}, status_code=404)

    # ✅ 確保是 list 且第一個元素存在
    if isinstance(result, list) and len(result) > 0 and 'ranking_list' in result[0]:
        return result[0]['ranking_list']
    else:
        return JSONResponse(content={"error": "Invalid ranking data format"}, status_code=500)