FROM python:3.11-slim

# 👉 設定台灣時區
ENV TZ=Asia/Taipei
RUN apt-get update && apt-get install -y tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get clean

# 工作目錄與檔案
WORKDIR /app
COPY . /app
# 移除 COPY .env（不從 repo 拷貝）
# COPY .env /app/.env

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 設定 Python 模組路徑
ENV PYTHONPATH=/app

# 啟動 FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
