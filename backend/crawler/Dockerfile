FROM python:3.11-slim

WORKDIR /app

ENV TZ Asia/Taipei

# 安裝套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼與 .env
COPY . .

# 預設執行主程式（可替換為你要跑的檔案）
CMD ["python", "run_daily_update.py"]
