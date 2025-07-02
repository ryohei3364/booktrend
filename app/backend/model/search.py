from ..database import db_pool
# from database import db_pool
from fastapi import *
from ..model.language import get_language_code
import fasttext

# backend % python -m model.search

model = fasttext.load_model('frontend/static/data/translate/lid.176.ftz')  # 需先下載模型檔案

def detect_language(request: Request, text):
    primary_code = get_language_code(request)
    labels, probabilities = model.predict(text, k=3)
    
    # 列出前3名語言及其機率，方便 debug
    print("🔍 Top 3 language predictions:")
    for label, prob in zip(labels, probabilities):
        # print(f"{label.replace('__label__', '')}: {prob:.4f}")
        # if prob < 0.5:
        #   return primary_code
        # 回傳第一名語言（最高機率）
        lang_code = labels[0].replace("__label__", "")
        return lang_code


def search(request: Request, keyword: str = None):
    if not keyword:
        return []

    keyword_lower = keyword.lower()
    print("搜尋關鍵字：", keyword_lower)

    lang_code = detect_language(request, keyword_lower)
    print("語言代碼：", lang_code)

    # ➤ 使用 SQL 進行模糊查詢
    query = """
    SELECT *,
        CASE
            WHEN LOWER(title) = %s THEN 1      -- 完全符合 title
            WHEN LOWER(title) LIKE %s THEN 2   -- 部分符合 title
            WHEN LOWER(description) LIKE %s THEN 3  -- 部分符合描述
            ELSE 4
        END AS match_priority
    FROM books
    WHERE LOWER(title) = %s
       OR LOWER(title) LIKE %s
       OR LOWER(description) LIKE %s
    ORDER BY match_priority
    """
    values = (
        keyword_lower,
        f"%{keyword_lower}%",
        f"%{keyword_lower}%",
        keyword_lower,
        f"%{keyword_lower}%",
        f"%{keyword_lower}%"
    )
    
    books = db_pool.get_cursor(query, values, fetch=True)

    if not books:
        return []

    # ➤ 使用第一本書的語言作為紀錄
    log_language = books[0]["language"] if books[0].get("language") else lang_code

    # ➤ 紀錄搜尋紀錄
    log_query = """
    INSERT INTO search_logs (keyword, language)
    VALUES (%s, %s)
    """
    db_pool.insert_cursor(log_query, (keyword_lower, log_language))
    return books

    
def hot_searches(request: Request):
    primary_code = get_language_code(request)
    print("語言代碼：", primary_code)
    
    query = """
    SELECT keyword, COUNT(*) AS count
    FROM search_logs
    WHERE language = %s
    GROUP BY keyword
    ORDER BY count DESC
    LIMIT 6;
    """
    return db_pool.get_cursor(query, (primary_code, ), fetch=True)
    
  

    