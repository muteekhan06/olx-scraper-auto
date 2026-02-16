# Base image
FROM python:3.10-slim

# Install system dependencies & Chrome
# We need wget, gnupg, curl, unzip for Chrome installation
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make entrypoint executable
RUN chmod +x railway_entrypoint.sh

# Set the entrypoint to handle secrets
ENTRYPOINT ["./railway_entrypoint.sh"]

# Default command (can be overridden by Railway Cron)
CMD ["python", "run_web.py"]
