# Base image
FROM python:3.10-slim

# ===== 1. Cài thư viện hệ thống =====
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxi6 \
    libxtst6 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# ===== 2. Cài Chrome headless =====
RUN curl -Lo /tmp/chrome.zip https://storage.googleapis.com/chrome-for-testing-public/121.0.6167.85/linux64/chrome-headless-shell-linux64.zip \
    && unzip /tmp/chrome.zip -d /opt/ \
    && rm /tmp/chrome.zip

# ===== 3. Cài Chromedriver =====
RUN curl -Lo /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/121.0.6167.85/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver.zip -d /opt/ \
    && rm /tmp/chromedriver.zip

# ===== 4. Set quyền =====
RUN chmod +x /opt/chrome-headless-shell-linux64/chrome-headless-shell
RUN chmod +x /opt/chromedriver-linux64/chromedriver

# ===== 5. Biến môi trường =====
ENV PATH="/opt/chromedriver-linux64:$PATH"

# ===== 6. Cài Python packages =====
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ===== 7. Copy source code =====
COPY . .

# ===== 8. Run app =====
CMD ["python", "main.py"]