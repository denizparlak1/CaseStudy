# Temel imaj olarak Python 3.8'i kullanalım
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8000", "app:app"]

EXPOSE 8000
