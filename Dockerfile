# -------- BUILD STAGE --------
FROM python:3.10-slim AS builder

WORKDIR /app

# 安裝必要系統套件（spaCy 的 zh/de 模型會需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 複製 requirements
COPY requirements.txt .

# 安裝 dependencies 到 /root/.local（減少 image 大小）
RUN pip install --upgrade pip && pip install --user --no-cache-dir -r requirements.txt


# 複製所有程式碼（改成你自己的）
COPY . .

# -------- FINAL STAGE --------
FROM python:3.10-slim

WORKDIR /app

# 複製上一步安裝好的套件
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 複製程式碼
COPY . .

# 設定啟動指令（可視你專案結構修改）
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "3000"]
