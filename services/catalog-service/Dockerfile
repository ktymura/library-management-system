FROM python:3.11-slim

# System deps (curl/wget do healthchecka)
RUN apt-get update && apt-get install -y --no-install-recommends wget && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Najpierw zależności (lepsze cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Potem kod
COPY . .

# Zmienne środowiskowe
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Domyślne wejście: uvicorn
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
