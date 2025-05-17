from fastapi import *
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app=FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
