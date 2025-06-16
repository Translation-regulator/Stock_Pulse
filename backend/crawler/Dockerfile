FROM python:3.11-slim

WORKDIR /app
ENV TZ=Asia/Taipei

# 安裝套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼（包含 .env 若 CI/CD 提供）
COPY . .

# 預設執行主程式（可在 docker run 時覆蓋）
CMD ["python", "run_daily_update.py"]
