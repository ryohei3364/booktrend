import json
from datetime import date
from ..database import db_pool
from dateutil.parser import parse

# terminal 執行: python -m backend.crawler.json_into_db_DE_yearly

# 假設你從某處獲得這個 JSON 字串
filename = 'fetch_DE_thalia_spiegel-1.json'
with open(filename, "r", encoding="utf-8") as f:
    book_list = json.load(f)

BOOKSTORE_NAME = 'thalia'

def get_or_create_author(name_de, name_original):
    query = "SELECT id FROM authors WHERE name_de = %s"
    result = db_pool.get_cursor(query, (name_de,), fetch=True)
    
    if result:
        return result[0]['id']

    insert = """
        INSERT INTO authors (name_original, name_de)
        VALUES (%s, %s)
    """
    db_pool.insert_cursor(insert, (name_original, name_de))
    
    result = db_pool.get_cursor(query, (name_de,), fetch=True)
    return result[0]['id']

def insert_book_if_not_exists(book_data, bookstore_id, author_id, published_date):
    check_query = "SELECT id FROM books WHERE title = %s AND bookstore_id = %s"
    exists = db_pool.get_cursor(check_query, (book_data["title"], bookstore_id), fetch=True)
    if exists:
        return exists[0]['id']

    insert_query = """
        INSERT INTO books (title, undertitle, original_title, bookstore_id, author_id, 
        image_url, book_url, isbn, publisher, published_date, description, language)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        book_data["title"],
        book_data["undertitle"],
        book_data["original_title"],
        bookstore_id,
        author_id,
        book_data["image_url"],
        book_data["url"],
        book_data["isbn"],
        book_data["publisher"],
        published_date,
        book_data["description"],
        "DE"
    )
    db_pool.insert_cursor(insert_query, values)

    # 回傳書籍 id
    result = db_pool.get_cursor(check_query, (book_data["title"], bookstore_id), fetch=True)
    return result[0]['id']
  
def get_or_create_category(name, bookstore_id, parent_id=None):
    # 查詢分類是否存在
    if name is None:
        return None
    else:
        query = "SELECT id FROM categories WHERE name = %s AND bookstore_id = %s"
        result = db_pool.get_cursor(query, (name, bookstore_id), fetch=True)
        
        if result:
            return result[0]['id']
        
        # 若不存在，插入
        insert = """
            INSERT INTO categories (bookstore_id, name, parent_id, path)
            VALUES (%s, %s, %s, %s)
        """
        db_pool.insert_cursor(insert, (bookstore_id, name, parent_id, ""))

        # 再查一次剛剛插入的 id
        result = db_pool.get_cursor(query, (name, bookstore_id), fetch=True)
        return result[0]['id']

def build_full_path(child_id):
    query = "SELECT id, parent_id FROM categories WHERE id = %s"
    parts = []
    current_id = child_id
    while current_id:
        result = db_pool.get_cursor(query, (current_id,), fetch=True)
        if result:
            parts.append(str(result[0]["id"]))
            current_id = result[0]["parent_id"]
        else:
            break
    return "/".join(reversed(parts))

def update_category_path(parent_id, child_id):
    path = build_full_path(child_id)
    update_query = "UPDATE categories SET path = %s WHERE id = %s"
    db_pool.insert_cursor(update_query, (path, child_id))

def insert_book_categories_if_not_exists(book_id, category_id):
    check_query = """
        SELECT 1 FROM book_categories
        WHERE book_id = %s AND category_id = %s
        LIMIT 1
    """
    result = db_pool.get_cursor(check_query, (book_id, category_id), fetch=True)
    
    if not result:
        insert_query = """
            INSERT INTO book_categories (book_id, category_id)
            VALUES (%s, %s)
        """
        db_pool.insert_cursor(insert_query, (book_id, category_id))
              
# def insert_category_translation_if_not_exists(category_id, language, name):
#     check_query = """
#         SELECT id FROM category_translations
#         WHERE category_id = %s AND language = %s
#     """
#     result = db_pool.get_cursor(check_query, (category_id, language), fetch=True)
    
#     if not result:
#         insert_query = """
#             INSERT INTO category_translations (category_id, language, name)
#             VALUES (%s, %s, %s)
#         """
#         db_pool.insert_cursor(insert_query, (category_id, language, name))

def insert_ranking_if_not_exists(title, ranking, bookstore_id, chart_type, chart_date):
    # 取得 book_id
    get_book_id = "SELECT id FROM books WHERE title = %s"
    book_result = db_pool.get_cursor(get_book_id, (title,), fetch=True)
    if not book_result:
        print(f"找不到書籍標題：{title}，跳過插入排名")
        return
    book_id = book_result[0]['id']

    # 檢查是否已存在相同紀錄
    check_query = """
        SELECT id FROM rankings
				WHERE book_id = %s AND bookstore_id = %s AND chart_type = %s AND chart_date = %s
    """
    exists = db_pool.get_cursor(check_query, (book_id, bookstore_id, chart_type, chart_date), fetch=True)
    
    if not exists:
        insert_query = """
            INSERT INTO rankings (ranking, book_id, bookstore_id, chart_type, chart_date)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (ranking, book_id, bookstore_id, chart_type, chart_date)
        db_pool.insert_cursor(insert_query, values)
        

get_bookstore_id = "SELECT id FROM bookstores WHERE name = %s"
bookstore_id = db_pool.get_cursor(get_bookstore_id, (BOOKSTORE_NAME,), fetch=True)[0]['id']
print(f"目前bookstore_id為:{bookstore_id}")

for book_data in book_list:  
    try:
        published_date = parse(book_data["publish_date"]).date()
    except Exception as e:
        print(f"無法解析出版日期：{book_data['title']} - {book_data['publish_date']}，錯誤：{e}")
        published_date = date(2000, 1, 1)  # 預設日期
    
    author_id = get_or_create_author(book_data["author"], book_data["origin_author"])
    book_id = insert_book_if_not_exists(book_data, bookstore_id, author_id, published_date)
    
    category_ids = []
    parent_id = None
    categories = book_data.get("categories") or []
    
    if not (1 <= len(book_data["categories"]) <= 5):
        print(f"分類層數異常：{book_data['title']} - {book_data['categories']}")
        continue

    # 動態處理 2~4 層分類
    for category_name in categories:
        category_id = get_or_create_category(category_name, bookstore_id, parent_id)
        if parent_id:  # 如果有上一層，更新 path
            update_category_path(parent_id, category_id)
        category_ids.append(category_id)
        parent_id = category_id  # 下一層分類的 parent_id

    # 書籍關聯每個分類節點
    for cid in category_ids:
        insert_book_categories_if_not_exists(book_id, cid)
 
    insert_ranking_if_not_exists(
        title=book_data["title"],
        ranking=book_data["rank"],
        bookstore_id=bookstore_id,
        chart_type="yearly",
        chart_date="2024-12-31"
    )