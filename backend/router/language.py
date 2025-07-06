from fastapi import Request, APIRouter
from ..model.language import get_language_code, get_language_data

language_router = APIRouter(prefix="/api/language", tags=["language"])

@language_router.get("")
def arrange_language_json(request: Request):
    data = get_language_data(request)
    return data