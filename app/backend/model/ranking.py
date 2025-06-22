from ..database import db_pool
from fastapi.responses import JSONResponse
from ..model.language import get_language_code
# from database import db_pool
from fastapi import *
import os, json

# backend % python -m model.ranking

def get_ranking_data(bookstore_id: int, chart_type: str):
    # 1️.先找出該 chart_type 的最新日期
    date_query = """
        SELECT MAX(chart_date)
        FROM rankings
        WHERE chart_type = %s AND bookstore_id = %s;
    """
    result = db_pool.get_cursor(date_query, (chart_type, bookstore_id), fetch=True)
    latest_date = result[0]["MAX(chart_date)"] if result else None

    if not latest_date:
        return []  # 沒有資料就回傳空清單

    # 2.再用這個日期抓排行榜內容
    data_query = """
        SELECT r.id, b.title, b.image_url, b.book_url, a.name AS author
        FROM rankings r
        JOIN books b ON r.book_id = b.id
        JOIN authors a ON b.author_id = a.id
        WHERE b.bookstore_id = %s AND r.chart_type = %s AND r.chart_date = %s
        ORDER BY r.ranking ASC;
    """
    return db_pool.get_cursor(data_query, (bookstore_id, chart_type, latest_date), fetch=True)

  
def get_ranking_list(request: Request):
    primary_code = get_language_code(request)
    # 支援的語言對應檔案
    lang_map = {
        "de": "de.json",
        "zh-tw": "zh.json",
        "en-us": "en.json",
        "fr": "fr.json",
    }
    filename = lang_map.get(primary_code)
    if filename:
        json_path = os.path.join("frontend/static/data/language", filename)
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
              data = json.load(f)
              return data

