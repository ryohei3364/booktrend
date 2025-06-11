from ..database import db_pool
# from database import db_pool
from fastapi import *
import json
from collections import Counter

# backend % python -m model.country_card

def get_description(bookstore_id: int):
  query = "SELECT description FROM books WHERE bookstore_id = %s"
  # query = """
  # SELECT GROUP_CONCAT(description SEPARATOR ' ') AS full_text
  # FROM books
  # WHERE bookstore_id = %s;
  # """
  return db_pool.get_cursor(query, (bookstore_id,), fetch=True)


def get_language_model(bookstore_id: int):
  if bookstore_id == 1:
    nlp = spacy.load("zh_core_web_sm")
    return nlp
  elif bookstore_id == 2:
    nlp = spacy.load("de_core_news_sm")
    return nlp
  elif bookstore_id == 3:
    nlp = spacy.load("de_core_news_sm")
    return nlp
  else:
    raise ValueError(f"Unsupported bookstore_id: {bookstore_id}")
      
      
def insert_wordcloud_data(bookstore_id: int):
  nlp = get_language_model(bookstore_id)
  data = get_description(bookstore_id)
  stopwords = {
    # 中文
    "作者", "作家", "這本", "什麼", "閱讀", "方法", "方式", "暢銷", "讀者", "可能", "不是", "一本", "我們",
    "就是", "自己", "可以", "本書", "推薦", "如果", "重要", "因為", "透過", "一個", "知道", "年度", "主持人",
    "創辦人", "系列", "這些"
    # 德文
    "und", "der", "von", "sie", "ein", "den", "mit", "in", "auf", "es", "das", "dem", "des", "im",
    "ihr", "einer", "aus", "einem", "Sie", "die", "uns", "Die", "für", "einen", "über", "it", "wir",
    "wie", "was", "ihrer", "ist", "In", "Mit", "Der", "Es", "er", "seinem", "eines", "man", "ihn",
    "aber", "vor", "le", "bis", "immer", "vom"
  }
  noun_counter = Counter()
  
  # if data and data[0].get('full_text'):
  #   description = data[0]['full_text']
  for book in data:
    description = book.get('description', '')
    doc = nlp(description)
    for token in doc:
      if token.pos_ == 'NOUN' and len(token.text) > 1 and token.text not in stopwords:
        noun_counter[token.text] += 1
  data = noun_counter.most_common(30)
  json_data = json.dumps(data, ensure_ascii=False)
  # print(json_data)
  query = """
  UPDATE bookstores SET wordcloud_json = %s WHERE id = %s
  """    
  db_pool.insert_cursor(query, (json_data, bookstore_id))


def generate_wordcloud(bookstore_id: int):
  query = "SELECT wordcloud_json FROM bookstores WHERE id = %s"    
  result = db_pool.get_cursor(query, (bookstore_id,), fetch=True)
  if not result or not result[0].get("wordcloud_json"):
    return []
  wordcloud_json = json.loads(result[0]["wordcloud_json"])
  return [{"text": word, "size": freq} for word, freq in wordcloud_json]
  

def generate_category(bookstore_id: int):
    # query = """
    # SELECT
    #   COALESCE(p.id, c.id) AS parent_category_id,
    #   COALESCE(p.name, c.name) AS parent_category_name,
    #   COUNT(DISTINCT bc.book_id) AS total_books
    # FROM book_categories bc
    # JOIN categories c ON bc.category_id = c.id
    # LEFT JOIN categories p ON c.parent_id = p.id
    # WHERE COALESCE(p.parent_id, c.parent_id) IS NULL
    #   AND (p.bookstore_id = %s OR c.bookstore_id = %s)
    # GROUP BY parent_category_id, parent_category_name
    # ORDER BY total_books DESC;
    # """
    query = """
    SELECT bc.category_id, c.name AS category_name, COUNT(bc.book_id) AS book_count
    FROM book_categories bc 
    JOIN categories c ON bc.category_id = c.id
    WHERE c.bookstore_id = %s 
    GROUP BY bc.category_id, c.name
    ORDER BY book_count DESC;
    """    
    # print(db_pool.get_cursor(query, (bookstore_id,), fetch=True))
    return db_pool.get_cursor(query, (bookstore_id,), fetch=True)


def generate_same_book(bookstore_id: int):
    query = """
    SELECT books.title, books.image_url, authors.name
    FROM books
    INNER JOIN authors ON books.author_id = authors.id
    WHERE books.group_id IS NOT NULL AND books.bookstore_id = %s
    """
    return db_pool.get_cursor(query, (bookstore_id,), fetch=True)
  

def generate_author(bookstore_id: int):
    query = """
    SELECT 
        a.id AS author_id,
        a.name AS author_name,
        COUNT(b.author_id) AS times
    FROM books b
    JOIN authors a ON b.author_id = a.id
    WHERE b.bookstore_id = %s
    GROUP BY a.id, a.name
    ORDER BY times DESC
    LIMIT 3;
    """
    # print(db_pool.get_cursor(query, (bookstore_id,), fetch=True))
    return db_pool.get_cursor(query, (bookstore_id,), fetch=True)
  
  
def generate_yearly(bookstore_id: int):
    # if bookstore_id == 3:
    #     return []  # 直接回傳空資料，避免查詢
    query = """
    SELECT 
      r.ranking,
      b.title,
      a.name,
      b.image_url
    FROM rankings r
    JOIN books b ON r.book_id = b.id
    JOIN authors a ON b.author_id = a.id
    WHERE r.ranking <= 3
      AND r.chart_type IN ('spiegel', 'yearly')
      AND r.bookstore_id = %s
    ORDER BY r.ranking;
    """
    # print(db_pool.get_cursor(query, (bookstore_id,), fetch=True))
    return db_pool.get_cursor(query, (bookstore_id,), fetch=True)


def generate_daily(bookstore_id: int):
    query = """
    SELECT 
      r.ranking,
      b.title,
      a.name,
      b.image_url
    FROM rankings r
    JOIN books b ON r.book_id = b.id
    JOIN authors a ON b.author_id = a.id
    WHERE r.ranking <= 3
      AND r.chart_type IN ('daily')
      AND r.bookstore_id = %s
    ORDER BY r.ranking;
    """
    # print(db_pool.get_cursor(query, (bookstore_id,), fetch=True))
    return db_pool.get_cursor(query, (bookstore_id,), fetch=True)
  
  
  
# if __name__ == "__main__":
#     print("Running wordcloud generation test...")
#     # bookstore_id = 1  # 測試用的書店 ID（請改成實際存在的）
#     generate_wordcloud(bookstore_id=1)
