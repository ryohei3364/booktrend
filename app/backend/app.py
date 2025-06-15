from fastapi import *
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
# from .database import db_pool
from .router.country_card import card_router
from .router.search import search_router
from .router.ranking import ranking_router
from .router.language import language_router
# from router.country_card import card_router
# from router.search import search_router
# from router.ranking import ranking_router
# from router.language import language_router
import os

app=FastAPI(redirect_slashes=True)

app.include_router(language_router)
app.include_router(card_router)
app.include_router(search_router)
app.include_router(ranking_router)
# templates = Jinja2Templates(directory="frontend/templates")
# app.mount("/static", StaticFiles(directory=os.path.join("frontend", "static")), name="static")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # BookTrend 根目錄
static_path = os.path.join(BASE_DIR, "frontend", "static")
templates_path = os.path.join(BASE_DIR, "frontend", "templates")

templates = Jinja2Templates(directory=templates_path)
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})

@app.get("/ranking", response_class=HTMLResponse)
async def ranking(request: Request):
    return templates.TemplateResponse("ranking.html", {"request": request})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開發中可用 "*"，正式環境請指定 domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_request_url(request: Request, call_next):
    print(f"👉 URL: {request.url}")
    response = await call_next(request)
    return response


print("Serving static from:", static_path)


# db_pool.check_processlist()

# # Static Pages (Never Modify Code in this Block)
# @app.get("/", include_in_schema=False)
# async def index(request: Request):
#     return FileResponse(os.path.join("frontend", "index.html"), media_type="text/html")

# @app.get("/search", include_in_schema=False)
# async def search(request: Request):
# 	return FileResponse(os.path.join("frontend", "search.html"), media_type="text/html")

# @app.get("/ranking", include_in_schema=False)
# async def search(request: Request):
# 	return FileResponse(os.path.join("frontend", "ranking.html"), media_type="text/html")
