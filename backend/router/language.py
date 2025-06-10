from fastapi import Request, APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os, json
from ..model.language import get_language


language_router = APIRouter(prefix="/api/language", tags=["language"])

@language_router.get("")
async def arrange_language(request: Request):
    result = await get_language(request)
    return result