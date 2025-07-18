from fastapi import *
import random
from ..model.country_card import generate_category, generate_wordcloud, generate_same_book, generate_author, generate_yearly, generate_daily

card_router = APIRouter(prefix="/api/card", tags=["card"])

@card_router.get("/category/{bookstore_id}")
async def get_cards_category(bookstore_id: int):
    raw_data = generate_category(bookstore_id)
    # 只取前 10 筆類別
    limited_data = raw_data[:10]
    # print(limited_data)

    # 提取 label 和數量
    labels = [item["category_name"] for item in limited_data]
    data = [item["book_count"] for item in limited_data]
    background_colors = [f"rgb({random.randint(0,255)},{random.randint(0,255)},{random.randint(0,255)})" for _ in range(len(labels))]

    chart_data = {
        "labels": labels,
        "datasets": [
            {
                "label": "書籍比例",
                "data": data,
                "backgroundColor": background_colors
            }
        ],
        # "translations":{
        #     "商業理財": "Business and Finance",
        #     "心理勵志": "Psychological Inspiration",
        #     "童書/青少年文學": "Children's Books/Youth Literature",
        #     "文學小說": "Literary Fiction",
        #     "漫畫/圖文書": "Comics/Picture Books", 
        #     "人文社科": "Humanities and Social Sciences",
        #     "宗教命理": "Religion and Numerology",
        #     "醫療保健": "Health Care",
        #     "生活風格": "Lifestyle",
        #     "國中小參考書": "Elementary and Middle School Reference Books"
        # }
    }
    return chart_data 


@card_router.get("/samebook/{bookstore_id}")
async def get_samebook(bookstore_id: int):
    return generate_same_book(bookstore_id)

@card_router.get("/author/{bookstore_id}")
async def get_author(bookstore_id: int):
    return generate_author(bookstore_id)

@card_router.get("/yearly/{bookstore_id}")
async def get_yearly(bookstore_id: int):
    return generate_yearly(bookstore_id)

@card_router.get("/daily/{bookstore_id}")
async def get_daily(bookstore_id: int):
    return generate_daily(bookstore_id)

@card_router.get("/wordcloud/{bookstore_id}")
async def wordcloud(bookstore_id: int):
    # data = await asyncio.to_thread(generate_wordcloud_data, bookstore_id)
    # return [{"text": word, "size": freq} for word, freq in data]    
    return generate_wordcloud(bookstore_id)
    

