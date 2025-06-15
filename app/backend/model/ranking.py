from ..database import db_pool
from fastapi.responses import JSONResponse
from ..model.language import get_language_code
# from database import db_pool
from fastapi import *
import os, json

# backend % python -m model.ranking

def get_ranking_data(bookstore_id: int, chart_type: str):
    query = """
		SELECT r.id, b.title, b.image_url, b.book_url, a.name AS author
		FROM rankings r
		JOIN books b ON r.book_id = b.id
		JOIN authors a ON b.author_id = a.id
		WHERE b.bookstore_id = %s AND r.chart_type = %s
		ORDER BY r.ranking ASC;
    """
    # print(db_pool.get_cursor(query, (bookstore_id, chart_type), fetch=True))
    return db_pool.get_cursor(query, (bookstore_id, chart_type), fetch=True)
  
def get_ranking_list(request: Request):
    primary_code = get_language_code(request)
    # 支援的語言對應檔案
    lang_map = {
        "de": "de.json",
        "tw": "zh.json",
        "zh": "zh.json",
        "en": "en.json",
        "fr": "fr.json",
    }
    filename = lang_map.get(primary_code)
    if filename:
        json_path = os.path.join("frontend/static/data/language", filename)
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
              data = json.load(f)
              return data

