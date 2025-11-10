# Use a modern, supported Python base (Debian bookworm slim)
FROM python:3.11-bookworm

# Set working directory
WORKDIR /app

# Avoid interactive prompts during apt installs
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (git + ffmpeg). Use apt-get and clean caches.
RUN apt-get update -y \
 && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python deps in requirements.txt (no cache)
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# If your bot needs a session string or other env vars, they must be passed through Render
# Example startup command — replace "bot.py" with your main script if different.
CMD ["python", "bot.py"]
