# Use a modern, supported Python base (Debian bookworm slim)
FROM python:3.11-bookworm

# Set working directory
WORKDIR /app

# Avoid interactive prompts during apt installs
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (git + ffmpeg)
RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ✅ IMPORTANT: Run the bot from main/__main__.py
CMD ["python", "-m", "main"]
