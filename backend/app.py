from fastapi import *
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
# from router.post import post_router
from database import db_pool

app=FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
# app.include_router(post_router)

db_pool.check_processlist()

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
