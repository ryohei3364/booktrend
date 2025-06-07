from fastapi import *
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from .database import db_pool
from .router.country_card import card_router
from .router.search import search_router
from .router.ranking import ranking_router
from .router.language import language_router
import os

app=FastAPI()
app.include_router(language_router)
app.include_router(card_router)
app.include_router(search_router)
app.include_router(ranking_router)

app.mount("/static", StaticFiles(directory=os.path.join("frontend", "static")), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開發中可用 "*"，正式環境請指定 domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_pool.check_processlist()

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
    return FileResponse(os.path.join("frontend", "index.html"), media_type="text/html")

@app.get("/search", include_in_schema=False)
async def search(request: Request):
	return FileResponse(os.path.join("frontend", "search.html"), media_type="text/html")

@app.get("/ranking", include_in_schema=False)
async def search(request: Request):
	return FileResponse(os.path.join("frontend", "ranking.html"), media_type="text/html")