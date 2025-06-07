# from ..database import db_pool
# from database import db_pool
from fastapi.responses import JSONResponse
from googletrans import Translator
# from difflib import SequenceMatcher
# from collections import defaultdict
import json, asyncio

# terminal backend %: python -m model.translate

translator = Translator()

async def translate_country_card(lang):
    with open('frontend/static/data/language/zh.json', encoding="utf-8") as f:
      data = json.load(f)
    
    # 翻譯每個值（假設值都是字串）
    translated_data = []
    
    for item in data:
      # 翻譯 country 名稱
      result = await translator.translate(item["country"], dest=lang)
      item["country"] = result.text
      
      # 翻譯 sections 中的 title 和 content
      for section in item.get("sections", []):
        if "title" in section:
          result = await translator.translate(section["title"], dest=lang)
          section["title"] = result.text
        if "content" in section and not section["content"].endswith(".png"):  # 避免翻譯圖片路徑
          result = await translator.translate(section["content"], dest=lang)
          section['content'] = result.text
          
      translated_data.append(item)
          
    with open(f'frontend/static/data/language/{lang}.json', "w", encoding="utf-8") as f:
      json.dump(translated_data, f, ensure_ascii=False, indent=2) 

# 在頂層使用 asyncio.run 呼叫非同步函式
if __name__ == "__main__":
    asyncio.run(translate_country_card("de"))
      

#     for row in authors:
#         author_id = row['id']
#         name = row['name']
#         lang = row['language']
        
#         if not name:
#             print(f"[跳過] id {author_id} 無 name")
#             continue
#         try:
#             result = translator.translate(name, src=lang, dest='en')
#             en_name = result.text.strip()             
#             print(f"[成功] {name} ({lang}) => {en_name}")

#             update_query = "UPDATE authors SET name_en = %s WHERE id = %s"
#             db_pool.get_cursor(update_query, (en_name, author_id))
#         except Exception as e:
#             print(f"[錯誤] {name} ({lang}) 翻譯失敗 => {e}")

#         time.sleep(0.5)

# if __name__ == "__main__":
#     translate_author_names()