# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 複製目錄
COPY . .

# 安裝套件
RUN pip install --no-cache-dir -r requirements.txt

# 設定環境變數讓模組 import 不出錯
ENV PYTHONPATH=/app

# 啟動 FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
