# 1) Start from an official Python image that already has pip
FROM python:3.10-slim

# 2) Install system-level dependencies (including curl, git, etc. if you need them)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      # if you ever need git or curl:
      git \
      curl \
 && rm -rf /var/lib/apt/lists/*

# 3) Set your working directory
WORKDIR /app

# 4) Copy just requirements.txt first (cache layer!)
COPY requirements.txt .

# 5) Upgrade pip and install Python deps via python -m pip
RUN python3 -m pip install --upgrade pip \
 && python3 -m pip install --no-cache-dir -r requirements.txt

# 6) Copy in the rest of your application code
COPY . .

# 7) Expose the port
ENV PORT=8000
EXPOSE 8000

# 8) Launch via Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
