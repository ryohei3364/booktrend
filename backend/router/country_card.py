from fastapi import *
from fastapi.responses import JSONResponse
import json, random, asyncio
from ..model.country_card import generate_category, generate_wordcloud_data, generate_same_book, generate_author, generate_yearly, generate_daily

card_router = APIRouter()

@card_router.get("/api/card")
async def get_cards():
    with open("backend/data/countryCard.json", encoding="utf-8") as f:
        data = json.load(f)
    return JSONResponse(content=data)


@card_router.get("/api/card/category/{bookstore_id}")
async def get_cards_category(bookstore_id: int):
    raw_data = generate_category(bookstore_id)
    # 只取前 10 筆類別
    limited_data = raw_data[:10]

    # 提取 label 和數量
    labels = [item["parent_category_name"] for item in limited_data]
    data = [item["total_books"] for item in limited_data]
    background_colors = [f"rgb({random.randint(0,255)},{random.randint(0,255)},{random.randint(0,255)})" for _ in range(len(labels))]

    chart_data = {
        "labels": labels,
        "datasets": [
            {
                "label": "書籍比例",
                "data": data,
                "backgroundColor": background_colors
            }
        ]
    }
    return chart_data 


@card_router.get("/api/card/samebook/{bookstore_id}")
async def get_samebook(bookstore_id: int):
    return generate_same_book(bookstore_id)

@card_router.get("/api/card/author/{bookstore_id}")
async def get_author(bookstore_id: int):
    return generate_author(bookstore_id)

@card_router.get("/api/card/yearly/{bookstore_id}")
async def get_yearly(bookstore_id: int):
    return generate_yearly(bookstore_id)

@card_router.get("/api/card/daily/{bookstore_id}")
async def get_daily(bookstore_id: int):
    return generate_daily(bookstore_id)

@card_router.get("/api/card/wordcloud/{bookstore_id}")
async def wordcloud(bookstore_id: int):
    data = await asyncio.to_thread(generate_wordcloud_data, bookstore_id)
    return [{"text": word, "size": freq} for word, freq in data]    

