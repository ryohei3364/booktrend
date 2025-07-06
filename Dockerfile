FROM python:3.10-slim

# 設定工作目錄為 /app
WORKDIR /app

# 安裝 build-essential 與 g++，確保支援 C++17
RUN apt-get update && apt-get install -y build-essential g++ \
    && rm -rf /var/lib/apt/lists/*
		
# 安裝 Python 套件
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# 複製整個 app 下的 backend 和 frontend（保持原本的資料夾位置）
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# 確保 backend 是 Python package（已加 __init__.py）
# 啟動 FastAPI，從 backend.app:app
# 本地測試在根目錄啟動 uvicorn.backend.app:app --reload
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "3000"]
