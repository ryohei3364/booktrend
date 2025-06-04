import json

json_file = "fetch_TW_books_daily_250528.json"

with open(json_file, 'r', encoding='utf-8') as file:
  data = json.load(file)

print(len(data))

# 依照 rank 排序（由小到大）
sorted_data = sorted(data, key=lambda x: x['rank'])

# 覆寫原始檔案或另存為新檔
with open(json_file, 'w', encoding='utf-8') as file:
    json.dump(sorted_data, file, ensure_ascii=False, indent=2)

print(f"{json_file} 已依照 rank 排序完成。")
  
