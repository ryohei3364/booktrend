from ..database import db_pool
# from database import db_pool
from fastapi import *
import json

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