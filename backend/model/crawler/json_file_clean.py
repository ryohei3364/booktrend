import requests, time, re, os, random, json
from datetime import datetime

filename = 'fetch_TW_books_year.json'
with open(filename, "r", encoding="utf-8") as f:
    book_data = json.load(f)
  
cleaned_books = []
for book in book_data:
    cleaned_book = {k.strip(): v for k, v in book.items()}
    cleaned_books.append(cleaned_book)
    
with open(filename, 'w', encoding='utf-8') as f:
    json.dump(cleaned_books, f, ensure_ascii=False, indent=2)

# 批次轉換日期格式
for book in book_data:
    if "publish_date" in book:
        try:
            parsed = datetime.strptime(book["publish_date"], "%d.%m.%Y")
            book["publish_date"] = parsed.strftime("%Y-%m-%d")
        except ValueError:
            print(f"⚠️ 無法解析日期: {book['publish_date']}")

for book in book_data:
    book['categories'] = book['categories'].replace('Startseite/Bücher/', '').split('/')

# 儲存修改後的 JSON
with open(filename, "w", encoding="utf-8") as f:
    json.dump(book_data, f, ensure_ascii=False, indent=2)
