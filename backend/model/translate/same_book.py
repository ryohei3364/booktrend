# from ..database import db_pool
from database import db_pool
from googletrans import Translator
# from difflib import SequenceMatcher
# from collections import defaultdict
import time
from rapidfuzz import fuzz

# terminal backend %: python -m model.translate

translator = Translator()
translated_cache = {}

def translate_author_names():
    query = """
        SELECT id, name, name_original, language FROM authors 
        WHERE name_en IS NULL
    """
    authors = db_pool.get_cursor(query, fetch=True)

    for row in authors:
        author_id = row['id']
        name = row['name']
        lang = row['language']
        
        if not name:
            print(f"[跳過] id {author_id} 無 name")
            continue
        try:
            result = translator.translate(name, src=lang, dest='en')
            en_name = result.text.strip()             
            print(f"[成功] {name} ({lang}) => {en_name}")

            update_query = "UPDATE authors SET name_en = %s WHERE id = %s"
            db_pool.get_cursor(update_query, (en_name, author_id))
        except Exception as e:
            print(f"[錯誤] {name} ({lang}) 翻譯失敗 => {e}")

        time.sleep(0.5)

if __name__ == "__main__":
    translate_author_names()


def translate_title(title):
    if title in translated_cache:
        return translated_cache[title]
    try:
        result = translator.translate(title, dest='en')
        translated = result.text
        translated_cache[title] = translated
        time.sleep(0.5)
        return translated
    except Exception as e:
        print(f"[翻譯錯誤] {title} 翻譯失敗: {e}")
        return title  # 若翻譯失敗，使用原本文字

def fetch_author_bookstore():
    query = """
        SELECT a.id, a.name_en, a.name_original, b.bookstore_id
        FROM authors a
        JOIN books b ON a.id = b.author_id
        WHERE a.name_en IS NOT NULL
    """
    return db_pool.get_cursor(query, fetch=True)


def get_titles_by_author_id(author_id):
    query = "SELECT title, original_title FROM books WHERE author_id = %s"
    rows = db_pool.get_cursor(query, (author_id,), fetch=True)
    return [(row["title"], row["original_title"])  for row in rows if row["title"]]  # 避免 None

    
def find_similar_authors():
    SIMILARITY_THRESHOLD = 80  # 可以根據需要調整相似度門檻
    records = fetch_author_bookstore()
    author_matches = []

    for i in range(len(records)):
        author_id_1 = records[i]["id"]
        name_en_1 = records[i]["name_en"]
        name_orig_1 = records[i]["name_original"]
        bookstore_id_1 = records[i]["bookstore_id"]

        for j in range(i+1, len(records)):
            author_id_2 = records[j]["id"]
            name_en_2 = records[j]["name_en"]
            name_orig_2 = records[j]["name_original"]
            bookstore_id_2 = records[j]["bookstore_id"]

            if author_id_1 == author_id_2 or bookstore_id_1 == bookstore_id_2:
                continue  # 排除自己或相同書店

            score_en_en = fuzz.token_sort_ratio(name_en_1, name_en_2)
            if score_en_en >= SIMILARITY_THRESHOLD:
                author_matches.append((author_id_1, name_en_1, bookstore_id_1,
                                       author_id_2, name_en_2, bookstore_id_2, score_en_en, "EN ↔ EN"))
                continue

            if name_orig_2:
                score_en_orig = fuzz.token_sort_ratio(name_en_1, name_orig_2)
                if score_en_orig >= SIMILARITY_THRESHOLD:
                    author_matches.append((author_id_1, name_en_1, bookstore_id_1,
                                           author_id_2, name_orig_2, bookstore_id_2, score_en_orig, "EN ↔ Original"))

            if name_orig_1:
                score_orig_en = fuzz.token_sort_ratio(name_orig_1, name_en_2)
                if score_orig_en >= SIMILARITY_THRESHOLD:
                    author_matches.append((author_id_1, name_orig_1, bookstore_id_1,
                                           author_id_2, name_en_2, bookstore_id_2, score_orig_en, "Original ↔ EN"))

    # 再比對書名
    print(f"\n🔍 找到 {len(author_matches)} 組相似作者：\n")
    print(author_matches)
    title_matches = []
    SIMILARITY_THRESHOLD = 60  # 可以根據需要調整相似度門檻

    for m in author_matches:
        titles_1 = get_titles_by_author_id(m[0])
        titles_2 = get_titles_by_author_id(m[3])
        print(titles_1, titles_2)

        best_score = 0
        best_pair = ("", "")
        for t1, o1 in titles_1:
            for t2, o2 in titles_2:
                t1_en = translate_title(t1)
                t2_en = translate_title(t2)
                
                score1 = fuzz.partial_token_sort_ratio(t1_en, t2_en)
                if score1 > best_score:
                    best_score = score1
                    best_pair = (t1 + " (翻)", t2 + " (翻)")

                if o1:
                    score2 = fuzz.partial_token_sort_ratio(o1, t2_en)
                    if score2 > best_score:
                        best_score = score2
                        best_pair = (o1 + " (原)", t2 + " (翻)")

                if o2:
                    score3 = fuzz.partial_token_sort_ratio(t1_en, o2)
                    if score3 > best_score:
                        best_score = score3
                        best_pair = (t1 + " (翻)", o2 + " (原)")

        if best_score >= SIMILARITY_THRESHOLD:
            title_matches.append((m[0], m[1], m[2], m[3], best_pair[0], best_pair[1], best_score))
        
    # 再比對書名
    print(f"\n🔍 找到 {len(title_matches)} 組相似書名：\n")
    print(title_matches)

if __name__ == "__main__":
    find_similar_authors()        
            


