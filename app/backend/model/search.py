from ..database import db_pool
# from database import db_pool
from fastapi import *
# from database import db_pool

# backend % python -m model.search

def search(keyword=None):
    if not keyword:
      return []
    
    keyword_lower = keyword.lower()
    
    # ➤ 特定關鍵字時，回傳 bookstore_id 全部書籍，不加 LIKE
    if keyword_lower in ['台灣', 'taiwan', '博客來']:
      query = "SELECT * FROM books WHERE bookstore_id = 1"
      return db_pool.get_cursor(query, fetch=True)
    
    elif keyword_lower in ['德國', 'germany', 'thalia']:
      query = "SELECT * FROM books WHERE bookstore_id = 2"
      return db_pool.get_cursor(query, fetch=True)

    # ➤ 一般搜尋：模糊查詢 title 和 description
    else:
      query = """
        SELECT * FROM books 
        WHERE title LIKE %s OR description LIKE %s
      """
      params = (f"%{keyword}%", f"%{keyword}%")
      return db_pool.get_cursor(query, params, fetch=True)
