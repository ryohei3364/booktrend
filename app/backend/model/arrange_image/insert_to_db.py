# from ..database import db_pool
from database import db_pool
from fastapi import *
from model.arrange_image import upload_to_s3

# backend % python -m model.arrange_image.insert_to_db

def insert_image():
    image_data = upload_to_s3.upload_all_images()
    
    if not image_data:
        print("沒有圖片需要更新")
        return

    query_update = "UPDATE books SET image_url_s = %s WHERE id = %s"
    query_check = "SELECT image_url_s FROM books WHERE id = %s"
    updated = 0
    skipped = 0
    
    for filename, url in image_data:
      try:
        book_id = int(filename.split("_")[-1].split(".")[0])

        # 檢查該筆是否已經有 image_url_s
        result = db_pool.get_cursor(query_check, (book_id,), fetch=True)
        current_url = result[0]['image_url_s'] if result else None

        if current_url:  # 已經有值就略過
          print(f"⏭️ 已存在縮圖，略過 book_id {book_id}")
          skipped += 1
          continue

        # 執行更新
        db_pool.get_cursor(query_update, (url, book_id))
        print(f"✅ 更新 book_id {book_id} 的縮圖網址")
        updated += 1

      except Exception as e:
        print(f"❌ 無法解析或更新: {filename}，錯誤：{e}")

    print(f"📦 共更新 {updated} 筆 image_url_s，略過 {skipped} 筆已有縮圖的書籍")
    
insert_image()