from ..database import db_pool
from fastapi import *
# from database import db_pool

# backend % python -m model.ranking

def get_ranking_data(bookstore_id: int, chart_type: str):
    query = """
		SELECT r.id, b.title, b.image_url_s, 
			CASE 
				WHEN b.bookstore_id = 1 THEN a.name
				WHEN b.bookstore_id = 2 THEN a.name
				ELSE a.name_original
			END AS author
		FROM rankings r
		JOIN books b ON r.book_id = b.id
		JOIN authors a ON b.author_id = a.id
		WHERE b.bookstore_id = %s AND r.chart_type = %s
		ORDER BY r.ranking ASC;
    """
    # print(db_pool.get_cursor(query, (bookstore_id, chart_type), fetch=True))
    return db_pool.get_cursor(query, (bookstore_id, chart_type), fetch=True)
  
  
  
