from fastapi import APIRouter
from ..model.ranking import get_ranking_data

ranking_router = APIRouter(prefix="/api/ranking", tags=["ranking"])

#/api/ranking?bookstore_id=xxx&chart_type=xxx
@ranking_router.get("")
async def get_rankings(bookstore_id:int, chart_type: str):
    result = get_ranking_data(bookstore_id, chart_type)
    return result[:10]