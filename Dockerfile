# ✅ Base image chuẩn AWS Lambda
FROM public.ecr.aws/lambda/python:3.10

# ===== 1. Cài thư viện hệ thống =====
RUN yum install -y \
    wget \
    unzip \
    curl \
    tar \
    gzip \
    shadow-utils \
    fontconfig \
    freetype \
    libX11 \
    libXcomposite \
    libXcursor \
    libXdamage \
    libXext \
    libXi \
    libXtst \
    cups-libs \
    libXScrnSaver \
    libXrandr \
    alsa-lib \
    atk \
    gtk3 \
    ipa-gothic-fonts \
    xorg-x11-fonts-100dpi \
    xorg-x11-fonts-75dpi \
    xorg-x11-fonts-cyrillic \
    xorg-x11-fonts-Type1 \
    xorg-x11-utils \
    && yum clean all

# ===== 2. Cài Chrome headless =====
RUN curl -Lo /tmp/chrome.zip https://storage.googleapis.com/chrome-for-testing-public/121.0.6167.85/linux64/chrome-headless-shell-linux64.zip \
    && unzip /tmp/chrome.zip -d /opt/ \
    && rm /tmp/chrome.zip

# ===== 3. Cài Chromedriver =====
RUN curl -Lo /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/121.0.6167.85/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chromedriver.zip -d /opt/ \
    && rm /tmp/chromedriver.zip

# ===== 4. Set quyền =====
RUN chmod +x /opt/chrome-headless-shell-linux64/chrome-headless-shell \
    && chmod +x /opt/chromedriver-linux64/chromedriver

# ===== 5. ENV (QUAN TRỌNG) =====
ENV CHROME_PATH=/opt/chrome-headless-shell-linux64/chrome-headless-shell
ENV CHROMEDRIVER_PATH=/opt/chromedriver-linux64/chromedriver
ENV PATH="/opt/chromedriver-linux64:$PATH"

# ===== 6. Python =====
WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ===== 7. Code =====
COPY . .

# ===== 8. Handler =====
CMD ["lambda_function.lambda_handler"]