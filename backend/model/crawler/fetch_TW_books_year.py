import requests, time, re, os, random, json
from bs4 import BeautifulSoup
import pandas as pd

# 目標網址
base_url = "https://www.books.com.tw"
start_url = "https://www.books.com.tw/web/annual100"
test_url = 'https://www.books.com.tw/products/0010945925?loc=P_0019_005'

# 設定請求標頭
headers = {
  "User-Agent": "Mozilla/5.0"
}
cookies = {
    "ssid": "681efed1a0f21.1748430745",
    "bid": "681efed1a0f21",
    "cid": "ryohei3364",
    "lpk": "ffeab00fe9f611b285b1d69a62c478c921d91a5d2aeff3d0e0f40d574e26fee6e2b580c60cbd0def",
    "pd": "3a9f0e07ea25173dbd31bd7d50bb3aacf226f4105276563960d1565fab0e802d342386212606d9b08c0ffa0ea8b0b1abfa62342273e59334254c9bb7dcbf03e9",
    "gud": "64f9efe6bfad5636825957a9759955888a4bc3fcec2b0b244cd8e6333acdb5e084b5e6dc58b3362656e8e9e77ca610e6e82193209c42635766cc8103b34fed2d",
    "bt": "swyyoj",
    "ltime": "2025%2F05%2F28+19%3A30%3A48"
}

# 定義排序鍵：抓網址中底線後的數字（例：0019_064 -> 64）
def extract_sort_key(url):
    pattern = re.search(r'_(\d+)$', url)
    return int(pattern.group(1)) if pattern else float('inf')
  
def get_book_links():
    response = requests.get(start_url, headers=headers, timeout=5)

    # 存下原始 HTML，方便檢查
    with open("debug.html", "w", encoding="utf-8") as f:
        f.write(response.text)
        
    if response.status_code != 200:
        print(f"請求失敗，狀態碼：{response.status_code}")
        return False
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        # 每本書的 a 標籤都在 class="table-td a" 內
        for li in soup.select("li.item"):
            a_tag = li.find("a", href=True)
            if a_tag:
                href = a_tag["href"]
                if href.startswith("https://www.books.com.tw/products/"):
                    links.append(href)
        
        unique_links = list(set(links))
        sorted_links = sorted(unique_links, key=extract_sort_key)
        
        # 儲存成 JSON
        with open("book_links_year.json", "w", encoding="utf-8") as f:
            json.dump(sorted_links, f, ensure_ascii=False, indent=2)
        
        print(f"共找到 {len(sorted_links)} 筆書籍連結，已儲存為 book_links_year.json")
        return sorted_links

get_book_links()


def get_book_info(url ,rank):
    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=5)
        time.sleep(5)
        if response.status_code != 200:
            print(f"請求失敗，狀態碼：{response.status_code}，網址：{url}")
            return None

        # # 存下原始 HTML，方便檢查
        # with open("debug.html", "w", encoding="utf-8") as f:
        #     f.write(response.text)

        soup = BeautifulSoup(response.text, 'html.parser')

        # 預設值
        title = undertitle = original_title = image_url = author = origin_author = ""
        isbn = publisher = publish_date = language = price = description = ""
        rating_average = rating_count = ""
        categories = []

        '''
        <div class="cnt_mod002 cover_img" id="M201106_0_getTakelook_P00a400020052">
        <img class="cover M201106_0_getTakelook_P00a400020052_image_wrap"
        src="https://im2.book.com.tw/image/getImage?i=https://www.books.com.tw/img/001/094/70/0010947051.jpg&v=63b6b4c6k&w=348&h=348"
        alt="我可能錯了：森林智者的最後一堂人生課">
        '''        # 選擇 class 包含 cover 的 <img>，用 CSS Selector
        # 原文書名
        price = soup.select_one("strong.price01").get_text(strip=True)
        
        try:
            original_title = soup.select_one(".grid_10 h2").get_text(strip=True)
        except:
            original_title = ''
            
        image_tag = soup.select_one("div.cnt_mod002.cover_img img.cover")
        if image_tag:
            image_url_src = image_tag.get("src")
            image_url_split = image_url_src.split("i=")[1]
            image_url = image_url_split.split(".jpg")[0] + ".jpg"
        else:
            print("image_tag 不存在")           
        # 書名
        title_tag = soup.select_one(".grid_10 h1")
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            if "：" in title_text:
                title, undertitle = title_text.split("：", 1)
            else:
                title = title_text
                undertitle = ""
        else:
            print("title_tag 不存在")    
        
        li_list = soup.select("div.type02_p003.clearfix ul li")  
        for li in li_list:
            text = li.get_text(strip=True)

            if "作者：" in text and not author:
                author = text.split("作者：")[-1].split("新功能介紹")[0].strip()

            elif "原文作者：" in text:
                origin_author = text.split("原文作者：")[-1].split("譯者：")[0].strip()

            elif "出版日期：" in text:
                publish_date = text.split("出版日期：")[-1].strip()

            elif "語言：" in text:
                language = text.split("語言：")[-1].strip()

            elif li.select_one("a span") and not publisher:
                publisher = li.select_one("a span").get_text(strip=True)
                 
        content = soup.select("div.mod_b.type02_m057.clearfix .content")
        if content:     
            description = content[0].get_text(strip=True)
            if origin_author == "":
                try:
                    origin_author_tag = content[1].get_text(strip=True)
                    match = re.search(r"（(.*?)）", origin_author_tag)
                    origin_author = match.group(1)
                except:
                    pass

        else:
            print("content 不存在")
            
        # 找到 breadcrumb trail
        breadcrumb = soup.select("#breadcrumb-trail li")

        # 取出分類標題（排除最後一個 li）
        categories = []
        for li in breadcrumb[2:-1]:  # 排除最後一個「商品介紹」
            a_tag = li.find("a")
            if a_tag:
                categories.append(a_tag.get_text(strip=True))
            
        details = soup.select("div.mod_b.type02_m058.clearfix .bd ul li")
        if details:               
            for ele in details:
                text = ele.get_text(strip=True)
                    
                if "ISBN：" in text:
                    match = re.search(r"ISBN：(\d+)", text)
                    isbn = match.group(1)
        else:
            print("details 不存在")
        
        try:    
            rating_average = soup.select_one("div.type02_p020 em.ratingValue").get_text(strip=True)
        except:   
            rating_average = ''
        try:
            rating_count_tag = soup.select_one("div.type02_p020 em.total")
            match = re.search(r"(\d+)", rating_count_tag.get_text())
            if match:
                rating_count = int(match.group(1))
        except:   
            rating_count = ''
                        
        data = {
            "rank": rank,
            "url": url,
            "title": title,
            "undertitle": undertitle,
            "original_title": original_title,
            "image_url": image_url,
            "author": author,
            "origin_author": origin_author,
            "isbn": isbn,
            "publisher": publisher,
            "publish_date": publish_date,
            "language": language,
            "price": price,
            "categories": categories,
            "rating_average": rating_average,
            "rating_count": rating_count,
            "description": description
        }
        return data
            
    except requests.ConnectionError as conn_ex:
        print("連線錯誤")
        print(str(conn_ex))
    except requests.Timeout as timeout_ex:
        print("請求超時錯誤")
        print(str(timeout_ex))
    except requests.RequestException as request_ex:
        print("請求發生錯誤")
        print(str(request_ex))
    except Exception as e:
        print("發生其它錯誤")
        print(str(e))

# # 測試 test_url 抓取資料
# book_info = get_book_info(test_url, rank=3)
# print(book_info)


def save_to_json(batch_data, filename):
    # 如果檔案存在，讀取並 append
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    else:
        existing_data = []
        
    # 建立已存在的 rank 集合，避免重複
    existing_ranks = {item["rank"] for item in existing_data}
    new_data = [item for item in batch_data if item["rank"] not in existing_ranks]

    # 加入新資料
    existing_data.extend(new_data)

    with open(filename, 'w', encoding='utf-8') as file:
        sorted_data = sorted(existing_data, key=lambda x: x['rank'])
        json.dump(sorted_data, file, ensure_ascii=False, indent=2)
        
        
json_file = "book_links_year.json"

with open(json_file, 'r', encoding='utf-8') as file:
  sorted_links = json.load(file)


def main():
    # sorted_links = get_book_links()
    if not sorted_links:
        print("未取得書籍連結")
        return
    print(f"共找到 {len(sorted_links)} 本書，開始抓取...\n")

    # 讀取已抓取資料筆數（繼續爬）
    json_file = "fetch_TW_books_yearly-1.json"
    processed_urls = set()
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
            processed_urls = {item["url"] for item in existing_data}
        print(f"已有 {len(processed_urls)} 筆資料，將跳過已處理的網址...\n")
    
    batch = []
    for idx, url in enumerate(sorted_links, start=1):
        if url in processed_urls:
            print(f"{idx}. 已抓取過，跳過：{url}")
            continue
        data = get_book_info(url, idx)
        if data:
            batch.append(data)
            print(f"{idx}. {data['title']} 抓取成功")
        else:
            print(f"{idx}. 抓取失敗：{url}")
        if idx % 2 == 0:
            print("每 2 筆儲存一次資料並休息 10 秒...")
            save_to_json(batch, filename=json_file)
            batch = []
            time.sleep(random.uniform(10, 15))
        else:
            time.sleep(random.uniform(10, 15))

    # 若剩下不足5筆的 batch 還沒儲存
    if batch:
        save_to_json(batch, filename=json_file)
        print("儲存最後一批的資料")
        
        
if __name__ == "__main__":
    main()        

