FROM python:3.10-slim

WORKDIR /app/backend

# 安裝 Python 套件
COPY backend/requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# 複製 backend 程式碼
COPY backend/ .

# 複製 frontend 靜態檔案到 backend/static 目錄
COPY frontend/ ./static/

# 啟動 FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "3000"]
