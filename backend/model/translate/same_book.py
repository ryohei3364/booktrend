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

    # # 3. 建立群組 (group_id 從 1 開始)，同時先插入 book_groups 表避免 FK 錯誤
    # for i, match in enumerate(title_matches, 1):
    #     author_id_1 = match[0]
    #     author_id_2 = match[3]
    #     group_id = i

    #     update_query = "UPDATE books SET group_id = %s WHERE author_id = %s"
    #     db_pool.get_cursor(update_query, (group_id, author_id_1))
    #     db_pool.get_cursor(update_query, (group_id, author_id_2))

if __name__ == "__main__":
    find_similar_authors()        
            
    
    # for row in results:
    #     id = row['id']
    #     name = row['name'] or ""
    #     name_original = row['name_original'] or ""
    #     name_en = row['name_en'] or ""
        
    #     # 分別對 name_en 與 name / name_original 比對
    #     score_name = fuzz.token_sort_ratio(name_en, name)
    #     score_original = fuzz.token_sort_ratio(name_en, name_original)

    #     if score_name >= SIMILARITY_THRESHOLD or score_original >= SIMILARITY_THRESHOLD:
    #         matches.append((id, name, name_original, name_en, max(score_name, score_original)))

    # 顯示比對結果
    # print(f"找到 {len(matches)} 組相似作者：\n")
    # for m in matches:
    #     print(f"[匹配] ({m[0]}) {m[1]}  <=>  ({m[2]}) {m[3]}  (相似度: {m[4]})")

# if __name__ == "__main__":
#     fuzzy_match_authors()

    
# def translate_titles(book_records, target_lang):
#     results = []
#     for book in book_records:
#         translated = translator.translate(book['title'], dest=target_lang).text.lower()
#         results.append({
#             "id": book["id"],
#             "original": book["title"],
#             "translated": translated,
#             "author": book["author_name"]
#         })
#     return results
  
# def find_duplicate_books(translated_books):
#     grouped = defaultdict(list)
#     for book in translated_books:
#         key = (book["translated"], book["author"])
#         grouped[key].append(book)

#     # 過濾出重複（相同標準化書名 + 作者）
#     duplicates = [group for group in grouped.values() if len(group) > 1]
#     return duplicates


# BATCH_SIZE = 100

# def fetch_titles(bookstore_id=None):
#     success_count = 0
#     error_count = 0

#     while True:
#         # SQL 有條件時才加入 bookstore_id 篩選
#         if bookstore_id is not None:
#             query = """
# 							SELECT bt.id, bt.title, bt.language
# 							FROM book_titles bt
# 							JOIN books b ON bt.book_id = b.id
# 							WHERE bt.en_title IS NULL AND b.bookstore_id = %s
# 							LIMIT %s
#             """
#             params = (bookstore_id, BATCH_SIZE)
#         else:
#             query = """
#                 SELECT id, title, language 
#                 FROM book_titles 
#                 WHERE en_title IS NULL
#                 LIMIT %s
#             """
#             params = (BATCH_SIZE,)

#         titles = db_pool.get_cursor(query, params, fetch=True)

#         if not titles:
#             print("✅ 所有標題都已翻譯完畢")
#             break

#         for row in titles:
#             title_id = row["id"]
#             title = row["title"]
#             lang = row["language"]

#             try:
#                 result = translator.translate(title, src=lang, dest="en")
#                 translated_title = result.text
#                 print(f"[成功] {title} ({lang}) => {translated_title}")

#                 update_query = "UPDATE book_titles SET en_title = %s WHERE id = %s"
#                 db_pool.get_cursor(update_query, (translated_title, title_id))
#                 success_count += 1

#             except Exception as e:
#                 print(f"[錯誤] {title} ({lang}) 翻譯失敗 => {e}")
#                 error_count += 1

#             time.sleep(0.3)  # 延遲避免封鎖

#     print(f"\n翻譯完成 ✅ 成功: {success_count}, 失敗: {error_count}")


# def main():
#     parser = argparse.ArgumentParser(description="翻譯 book_titles 中尚未翻譯的標題")
#     parser.add_argument("--bookstore_id", type=int, help="指定書店ID進行翻譯")

#     args = parser.parse_args()

#     fetch_titles(bookstore_id=args.bookstore_id)

# if __name__ == "__main__":
#     main()

