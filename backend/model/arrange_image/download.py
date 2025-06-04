import requests, os
# from ..database import db_pool
# from fastapi import *
from database import db_pool
from PIL import Image

def ensure_folder(folder):
  os.makedirs(folder, exist_ok=True)
  return folder

def download_image(bookstore_id, folder='images'):
  ensure_folder(folder)
  query = "SELECT id, image_url FROM books WHERE bookstore_id = %s"
  books = db_pool.get_cursor(query, (bookstore_id,), fetch=True)

  for book in books:
    id = book['id']
    url = book['image_url']
    path = os.path.join(folder, f"book_{id}.jpg")
    if os.path.exists(path):
      print(f"⏭️ 已存在，略過: {path}")
      continue
    try:
      res = requests.get(url)
      if res.status_code == 200:
        path = os.path.join(folder, f"book_{id}.jpg")
        with open(path, 'wb') as f:
          f.write(res.content)
        print(f"✅ Downloaded: {path}")
      else:
        print(f"❌ 下載失敗（狀態碼 {res.status_code}）book_id={id}")
    except Exception as e:
      print(f"❌ 發生錯誤：book_id={id}, error={e}")
          
download_image(2)      # 下載 bookstore_id 為 1 的書籍圖片

def resize_image(file_path, out_folder="resized", max_size=(150, 300)):
  try:
    img = Image.open(file_path)  
    # 計算等比例縮放的尺寸，保證在 max_width 和 max_height 框內
    img.thumbnail(max_size, Image.LANCZOS)
    ensure_folder(out_folder)

    # 拿原始檔名來命名
    filename = os.path.basename(file_path)
    out_path = os.path.join(out_folder, f"resized_{filename}")
    img.save(out_path, quality=100)
    print(f"✅ Resized: {out_path}")
  except Exception as e:
    print(f"❌ Resize error: {file_path}, {e}")
    
def resize_all(folder="images"):
  for file in os.listdir(folder):
    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
      resize_image(os.path.join(folder, file))
      
resize_all()    # 把 images 資料夾裡所有圖片 resize 存到 resized/
            
