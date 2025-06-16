FROM python:3.11-slim

WORKDIR /app

ENV TZ=Asia/Taipei

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run_daily_update.py"]
