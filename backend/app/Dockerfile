FROM python:3.11-slim

ENV TZ=Asia/Taipei
RUN apt-get update && apt-get install -y tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && apt-get clean

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
