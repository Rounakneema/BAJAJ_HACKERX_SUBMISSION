FROM python:3.10-slim

# 1) Install build deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

# 2) Set working directory
WORKDIR /app

# 3) Copy Python dependencies and install them
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip \
 && python3 -m pip install --no-cache-dir -r requirements.txt

# 4) Copy your application code (including app/__init__.py)
COPY . .

# 5) Expose port
EXPOSE 8000

# 6) Use sh -c so $PORT is expanded at runtime
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
