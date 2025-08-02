FROM python:3.10-slim

# Install any build deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy & install Python deps
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip \
 && python3 -m pip install --no-cache-dir -r requirements.txt

# Copy your app code
COPY . .

# Expose for documentation (Railway will wire up its own port)
EXPOSE 8000

CMD [ "sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000" ]
