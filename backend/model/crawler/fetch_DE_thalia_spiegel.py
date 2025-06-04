from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time, json, os, random
  
def get_thalia_links():
    options = Options()
    # options.add_argument("--headless")  # 無頭模式
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # 啟動瀏覽器
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = "https://www.thalia.de/themenwelten/spiegel-bestseller"
    driver.get(url)
    
    # 等待 JS 加載（必要）
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    links = []

    for a in soup.select('.tm-produktliste-wrapper li a'):
        href = a.get("href")
        if href and href.startswith("/shop/home/"):
            full_link = "https://www.thalia.de" + href
            links.append(full_link)

    driver.quit()

    # 去重並保留順序
    links = list(dict.fromkeys(links))
    # grouped_links = [links[i:i+20] for i in range(0, len(links), 20)]

    # 直接存整個列表，不分組、不分類
    with open("thalia_bestseller_links.json", "w", encoding="utf-8") as f:
        json.dump(links, f, ensure_ascii=False, indent=2)

    print("thalia_bestseller_links.json")
    return links

# get_thalia_links()
  
  
def get_book_details(url, rank):
    options = Options()
    # options.add_argument("--headless")  # 無頭模式
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # 啟動瀏覽器
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        image_tags = driver.find_elements(By.CSS_SELECTOR, 'tab-panel[data-tab="bilder"] picture img')
        image_urls = [img.get_attribute("src") for img in image_tags]
        img_url = image_urls[0] if image_urls else ""

        title_tag = driver.find_element(By.XPATH, '//h1[contains(@class, "element-headline-medium titel")]')
        # 只取 h1 標籤的主要文字（不包含 span）
        title = title_tag.get_attribute("innerText").split("\n")[0].strip()
        
        
        try:
            undertitle = ""
            undertitle_element = title_tag.find_element(By.CSS_SELECTOR, 'span.element-text-standard.untertitel')
            undertitle = undertitle_element.text.strip()
        except:
            undertitle = ""
        
        try:
            author_tag = driver.find_element(By.XPATH, '//li[contains(@class, "autor")]//a')
            author = author_tag.text
        except:
            author = ""
        
        try:
            rating_average_tag = driver.find_element(By.XPATH, '//span[contains(@class, "element-rating-standard")]')
            rating_average = rating_average_tag.get_attribute('rating')
        except:
            rating_average = ""

        try:
            rating_count_tag = driver.find_element(By.XPATH, '//span[contains(@class, "element-link-standard")]')
            rating_count = rating_count_tag.text
        except:
            rating_count = ""
            
        price_tag = driver.find_element(By.XPATH, '//div[contains(@class, "preis")]//p')
        price = price_tag.text
        
        description = ""
        # 抓取 Beschreibung 區塊
        desc_div = soup.select_one("section.zusatztext div.element-text-standard")

        if desc_div:
            description = desc_div.get_text(strip=True)
        else:
            print("找不到 desc_div")
        
        # 尋找所有 detail 區塊
        publish_date = ""
        publisher = ""
        language = ""
        isbn = ""
        for section in soup.select("div.artikeldetails section.artikeldetail"):
            key_elem = section.select_one("h3.detailbezeichnung")
            if not key_elem:
                continue
            key = key_elem.get_text(strip=True)
            # print(f"key = {key}")

            # 根據 key 對應到你想要的欄位
            if key == "Erscheinungsdatum":
                value_elem = section.select_one("p.single-value")
                publish_date = value_elem.get_text(strip=True) if value_elem else ""
            elif key == "Verlag":
                value_elem = section.select_one("a")
                publisher = value_elem.get_text(strip=True) if value_elem else ""
            elif key == "Sprache":
                value_elem = section.select_one("p.single-value")
                language = value_elem.get_text(strip=True) if value_elem else ""
            elif key == "ISBN":
                value_elem = section.select_one("p.single-value")
                isbn = value_elem.get_text(strip=True) if value_elem else ""

        # 解析分類區塊
        for li in soup.select("ul.breadcrumb-list"):
            li_tags = li.get_text(strip=True)
            
        data = {
            "rank": rank,
            "url": url,
            "title": title,
            "undertitle": undertitle,
            "original_title": "",
            "image_url": img_url,
            "author": author,
            "origin_author": "",
            "isbn": isbn,
            "publisher": publisher,
            "publish_date": publish_date,
            "language": language,
            "price": price,
            "categories": li_tags,
            "rating_average": rating_average,
            "rating_count": rating_count,
            "description": description
        }
        return data
            
    except Exception as e:
        print("發生其它錯誤")
        print(str(e))
            

    finally:
        driver.quit()

# # # 使用範例
# # url = 'https://www.thalia.de/shop/home/artikeldetails/A1073410729'
# # book_data = get_book_details(url, 1)
# # print(book_data)


def save_to_json(batch_data, filename):
    # 如果檔案存在，讀取並 append
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    else:
        existing_data = []

    existing_data.extend(batch_data)

    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=2)
        
        
json_file = "thalia_bestseller_links.json"

with open(json_file, 'r', encoding='utf-8') as file:
  links = json.load(file)
  
def main():
    # links = get_thalia_links()
    if not links:
        print("未取得書籍連結")
        return
    print(f"共找到 {len(links)} 本書，開始抓取...\n")

    # 讀取已抓取資料筆數（繼續爬）
    processed_count = 0
    json_file = "fetch_DE_thalia_spiegel-1.json"
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
            processed_count = len(existing_data)
        print(f"已有 {processed_count} 筆資料，從第 {processed_count+1} 本開始...\n")
    
    batch = []
    
    for idx, url in enumerate(links[processed_count:], start=processed_count+1):
        data = get_book_details(url, idx)
        if data:
            batch.append(data)
            print(f"{idx}. {data['title']} 抓取成功")
        else:
            print(f"{idx}. 抓取失敗：{url}")

        if idx % 2 == 0:
            print("每 2 筆儲存一次資料並休息 10 秒...")
            save_to_json(batch, filename=json_file)
            batch = []
            time.sleep(random.uniform(5, 8))
        else:
            time.sleep(random.uniform(5, 8))

    # 若剩下不足5筆的 batch 還沒儲存
    if batch:
        save_to_json(batch, filename=json_file)
        print("儲存最後一批的資料")


if __name__ == "__main__":
    main()        

