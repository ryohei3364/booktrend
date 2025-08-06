from ..database import db_pool
# from database import db_pool
from fastapi import *
import json
from collections import Counter

# backend % python -m model.country_card

def get_description(bookstore_id: int):
  query = "SELECT description FROM books WHERE bookstore_id = %s"
  return db_pool.get_cursor(query, (bookstore_id,), fetch=True)


def generate_wordcloud(bookstore_id: int):
  query = "SELECT wordcloud_json FROM bookstores WHERE id = %s"    
  result = db_pool.get_cursor(query, (bookstore_id,), fetch=True)
  if not result or not result[0].get("wordcloud_json"):
    return []
  wordcloud_json = json.loads(result[0]["wordcloud_json"])
  return [{"text": word, "size": freq} for word, freq in wordcloud_json]
  

def generate_category(bookstore_id: int):
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
    WHERE b.bookstore_id = %s AND a.id NOT IN (400, 963)
    GROUP BY a.id, a.name
    ORDER BY times DESC
    LIMIT 3;
    """
    return db_pool.get_cursor(query, (bookstore_id,), fetch=True)
  
  
def generate_yearly(bookstore_id: int):
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
      AND r.chart_type IN ('yearly')
      AND r.bookstore_id = %s
      AND r.chart_date = (
        SELECT MAX(chart_date)
        FROM rankings
        WHERE chart_type IN ('yearly')
          AND bookstore_id = %s
      )
    ORDER BY r.ranking;
    """
    # print(db_pool.get_cursor(query, (bookstore_id,), fetch=True))
    return db_pool.get_cursor(query, (bookstore_id, bookstore_id), fetch=True)


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
      AND r.chart_type = 'daily'
      AND r.bookstore_id = %s
      AND r.chart_date = (
        SELECT MAX(chart_date)
        FROM rankings
        WHERE chart_type = 'daily'
          AND bookstore_id = %s
      )
    ORDER BY r.ranking;
    """
    # print(db_pool.get_cursor(query, (bookstore_id,), fetch=True))
    return db_pool.get_cursor(query, (bookstore_id, bookstore_id), fetch=True)
  
  
  
# if __name__ == "__main__":
#     print("Running wordcloud generation test...")
#     # bookstore_id = 1  # 測試用的書店 ID（請改成實際存在的）
#     generate_wordcloud(bookstore_id=1)
